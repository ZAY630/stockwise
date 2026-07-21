"""Multi-Agent Orchestrator — coordinates the three StockWise agents.

Handles:
- Query classification (single vs. multi-agent)
- Agent routing (which agent handles what)
- Multi-agent orchestration (parallel and sequential pipelines)
- Synthesis of multi-agent findings into a unified recommendation
"""

import asyncio
import time
from enum import Enum

from anthropic import AsyncAnthropic

from app.agents.base import AgentContext
from app.agents.financial_agent import FinancialReportAgent
from app.agents.market_agent import MarketDataAgent
from app.agents.news_agent import NewsAnalysisAgent
from app.agents.prompts import ORCHESTRATOR_SYNTHESIS_PROMPT
from app.config import settings

# Simple in-memory analysis cache (TTL-based)
_analysis_cache: dict[str, tuple[float, dict]] = {}


class OrchestrationMode(Enum):
    SINGLE = "single"         # One agent handles the query
    PARALLEL = "parallel"     # All agents run independently, results synthesized
    SEQUENTIAL = "sequential" # News → Financial → Market (each receives prior context)


class MultiAgentOrchestrator:
    """Routes queries to agents and coordinates multi-agent workflows."""

    def __init__(self, client: AsyncAnthropic):
        self.client = client
        self.financial = FinancialReportAgent(client)
        self.news = NewsAnalysisAgent(client)
        self.market = MarketDataAgent(client)

    async def route_and_execute(
        self,
        query: str,
        symbol: str | None = None,
        mode: OrchestrationMode | None = None,
        force_agent: str | None = None,
    ) -> dict:
        """Main entry point — route query and execute appropriate agent(s).

        Results are cached by (symbol, mode, force_agent) for 10 minutes.
        """
        # Check cache first (query hash prevents collision between different questions)
        import hashlib
        query_hash = hashlib.md5(query.encode()).hexdigest()[:8]
        cache_key = f"{symbol or 'no_symbol'}:{mode.value if mode else 'auto'}:{force_agent or 'none'}:{query_hash}"
        now = time.time()
        if cache_key in _analysis_cache:
            expiry, cached_result = _analysis_cache[cache_key]
            if now < expiry:
                return cached_result

        ctx = AgentContext(symbol=symbol.upper() if symbol else None, user_query=query)
        result: dict

        # Force a specific agent
        if force_agent:
            agent = {"financial": self.financial, "news": self.news, "market": self.market}[force_agent]
            analysis = await agent.analyze(ctx)
            result = {"mode": "single", "agent": agent.name, "result": analysis}
        else:
            # Auto-detect mode
            if mode is None:
                mode = self._classify_query(query)

            if mode == OrchestrationMode.SINGLE:
                agent = self._select_agent(query)
                analysis = await agent.analyze(ctx)
                result = {"mode": "single", "agent": agent.name, "result": analysis}

            elif mode == OrchestrationMode.PARALLEL:
                results = await asyncio.gather(
                    self.financial.analyze(ctx),
                    self.news.analyze(ctx),
                    self.market.analyze(ctx),
                )
                ctx.news_sentiment = results[1]
                ctx.financial_summary = results[0]
                ctx.market_data = results[2]
                synthesis = await self._synthesize(ctx, results)
                result = {"mode": "parallel", "results": results, "synthesis": synthesis}

            elif mode == OrchestrationMode.SEQUENTIAL:
                news_result = await self.news.analyze(ctx)
                ctx.news_sentiment = news_result
                financial_result = await self.financial.analyze(ctx)
                ctx.financial_summary = financial_result
                market_result = await self.market.analyze(ctx)
                ctx.market_data = market_result
                results = [news_result, financial_result, market_result]
                synthesis = await self._synthesize(ctx, results)
                result = {"mode": "sequential", "results": results, "synthesis": synthesis}
            else:
                result = {"mode": "unknown", "result": "Could not classify query"}

        # Cache for 10 minutes
        _analysis_cache[cache_key] = (now + 600, result)
        return result

    def _classify_query(self, query: str) -> OrchestrationMode:
        """Classify whether a query needs a single agent or multi-agent analysis."""
        q = query.lower()

        multi_keywords = [
            "should i invest", "is it a good time", "comprehensive",
            "full analysis", "complete picture", "recommend",
            "all aspects", "everything about", "deep dive",
            "should i buy", "should i sell", "what do you think about",
            "analyze", "evaluate", "assess",
        ]
        if any(kw in q for kw in multi_keywords):
            return OrchestrationMode.SEQUENTIAL

        return OrchestrationMode.SINGLE

    def _select_agent(self, query: str):
        """Route to the most appropriate single agent based on keywords."""
        q = query.lower()

        financial_kw = [
            "revenue", "earnings", "balance sheet", "income", "sec", "10-k", "10-q",
            "financial", "cash flow", "debt", "profit", "p/e", "ratio", "margin",
            "quarterly", "annual report", "filing", "ebitda", "roe", "roa",
        ]
        news_kw = [
            "news", "headline", "sentiment", "announcement", "report says",
            "recently", "happened", "event", "rumor",
        ]
        market_kw = [
            "price", "chart", "rsi", "macd", "moving average", "trend", "volume",
            "support", "resistance", "indicator", "technical", "overbought",
            "oversold", "bollinger", "graph",
        ]

        if any(kw in q for kw in financial_kw):
            return self.financial
        elif any(kw in q for kw in news_kw):
            return self.news
        else:
            return self.market  # Default to market data

    async def _synthesize(self, ctx: AgentContext, agent_results: list[str]) -> str:
        """Synthesize multi-agent outputs into a unified recommendation.

        Uses a separate Claude call with the orchestrator synthesis prompt
        to combine all three perspectives.
        """
        parts = [
            f"**User's question:** {ctx.user_query}",
            f"**Stock:** {ctx.symbol or 'Not specified'}",
            "",
            "**News Analysis Agent found:**",
            agent_results[0] if len(agent_results) > 0 else "No news analysis available",
            "",
            "**Financial Report Agent found:**",
            agent_results[1] if len(agent_results) > 1 else "No financial analysis available",
            "",
            "**Market Data Agent found:**",
            agent_results[2] if len(agent_results) > 2 else "No market analysis available",
            "",
            "Synthesize these into a unified, beginner-friendly analysis with a clear recommendation.",
        ]

        user_message = "\n".join(parts)

        try:
            response = await self.client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=16000,
                system=ORCHESTRATOR_SYNTHESIS_PROMPT,
                messages=[{"role": "user", "content": user_message}],
            )

            text_output = []
            for block in response.content:
                if block.type == "text":
                    text_output.append(block.text)
                elif block.type == "thinking":
                    pass  # Skip thinking blocks in synthesis output
            result = "".join(text_output)
            if result:
                return result
            return "Synthesis completed but no text was generated."
        except Exception as e:
            return f"Synthesis failed: {str(e)}\n\nIndividual agent results are available above."


# Singleton orchestrator instance
_orchestrator: MultiAgentOrchestrator | None = None


async def get_orchestrator() -> MultiAgentOrchestrator:
    """Get or create the singleton orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        _orchestrator = MultiAgentOrchestrator(client)
    return _orchestrator
