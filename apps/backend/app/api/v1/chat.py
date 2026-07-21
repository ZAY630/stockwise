"""Chat endpoints with SSE streaming support."""

import asyncio
import json

from fastapi import APIRouter, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from app.agents.orchestrator import OrchestrationMode, get_orchestrator
from app.schemas.chat import ChatRequest

router = APIRouter()


@router.post("")
async def chat(request: ChatRequest):
    """Send a chat message and get an agent response.

    Includes conversation history so the agent remembers previous exchanges.
    """
    try:
        orchestrator = await get_orchestrator(request.api_key)

        # Build query with conversation history for context
        query_with_history = request.query
        if request.history and len(request.history) > 0:
            history_text = "\n".join(
                f"[{m.get('role', 'unknown')}]: {m.get('content', '')}"
                for m in request.history[-10:]  # Last 10 messages
            )
            query_with_history = (
                f"Previous conversation:\n{history_text}\n\n"
                f"Current question: {request.query}\n\n"
                f"Please respond to the current question, taking into account the conversation context above."
            )

        if request.stream:
            return EventSourceResponse(
                _stream_chat_response(orchestrator, query_with_history, request.symbol)
            )

        # Non-streaming response
        result = await orchestrator.route_and_execute(
            query=query_with_history,
            symbol=request.symbol.upper() if request.symbol else None,
        )
        return {
            "query": request.query,
            "mode": result.get("mode", "single"),
            "response": result.get("synthesis", result.get("result", "")),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _stream_chat_response(orchestrator, query: str, symbol: str | None):
    """Generate SSE stream for chat response."""
    try:
        # Classify the query
        mode = orchestrator._classify_query(query)

        if mode == OrchestrationMode.SINGLE:
            agent = orchestrator._select_agent(query)
            yield {
                "event": "status",
                "data": json.dumps({"agent": agent.name, "status": "analyzing"}),
            }

            from app.agents.base import AgentContext

            ctx = AgentContext(symbol=symbol.upper() if symbol else None, user_query=query)
            result = await agent.analyze(ctx)

            yield {
                "event": "message",
                "data": json.dumps({"agent": agent.name, "content": result}),
            }
        else:
            # Multi-agent: run sequentially and stream each agent's output
            from app.agents.base import AgentContext

            ctx = AgentContext(symbol=symbol.upper() if symbol else None, user_query=query)

            agents = [
                ("News Analysis Agent", orchestrator.news),
                ("Financial Report Agent", orchestrator.financial),
                ("Market Data Agent", orchestrator.market),
            ]

            agent_results = []
            for agent_name, agent in agents:
                yield {
                    "event": "status",
                    "data": json.dumps({"agent": agent_name, "status": "analyzing"}),
                }

                result = await agent.analyze(ctx)
                agent_results.append(result)

                yield {
                    "event": "message",
                    "data": json.dumps({"agent": agent_name, "content": result}),
                }

                # Update context for next agent
                if agent_name == "News Analysis Agent":
                    ctx.news_sentiment = result
                elif agent_name == "Financial Report Agent":
                    ctx.financial_summary = result
                elif agent_name == "Market Data Agent":
                    ctx.market_data = result

                await asyncio.sleep(0.5)  # Brief pause between agents

            # Synthesis
            yield {
                "event": "status",
                "data": json.dumps({"agent": "Orchestrator", "status": "synthesizing"}),
            }

            synthesis = await orchestrator._synthesize(ctx, agent_results)

            yield {
                "event": "message",
                "data": json.dumps({"agent": "Orchestrator", "content": synthesis}),
            }

        yield {"event": "done", "data": json.dumps({"status": "complete"})}

    except Exception as e:
        yield {
            "event": "error",
            "data": json.dumps({"error": str(e)}),
        }
