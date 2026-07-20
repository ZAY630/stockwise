"""Base agent class implementing the Claude API agentic loop.

All specialized agents extend this class. The loop:
1. Send user message + context to Claude with tool definitions
2. If Claude returns text (end_turn), return it
3. If Claude returns tool_use blocks, execute them in parallel
4. Send tool results back to Claude, repeat
"""

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any

from anthropic import AsyncAnthropic

from app.config import settings


@dataclass
class AgentContext:
    """Shared context passed between agents during multi-agent collaboration.

    Each agent populates its findings into this context object,
    which subsequent agents can read for additional perspective.
    """

    symbol: str | None = None
    user_query: str = ""
    financial_summary: str | None = None
    news_sentiment: str | None = None
    market_data: str | None = None
    intermediate_notes: list[str] = field(default_factory=list)


class BaseAgent:
    """Base agent with Claude API tool-use loop.

    Subclasses define:
    - name: str
    - system_prompt: str
    - tools: list[dict] (JSON Schema tool definitions)
    """

    name: str = "base"
    system_prompt: str = ""
    tools: list[dict] = []

    def __init__(self, client: AsyncAnthropic, model: str | None = None):
        self.client = client
        self.model = model or settings.ANTHROPIC_MODEL

    async def analyze(self, context: AgentContext) -> str:
        """Run the agentic loop against Claude.

        Args:
            context: AgentContext with symbol, user query, and any prior agent findings.

        Returns:
            The final text response from Claude.
        """
        messages: list[dict[str, Any]] = [
            {"role": "user", "content": self._build_user_message(context)}
        ]

        max_turns = 10  # Safety limit to prevent infinite loops
        for _ in range(max_turns):
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=16000,
                system=self.system_prompt,
                tools=self.tools,
                messages=messages,
            )

            # Filter out thinking blocks — APIs reject them in conversation history
            clean_content = [b for b in response.content if b.type != "thinking" and b.type != "redacted_thinking"]

            # Check stop reason
            if response.stop_reason == "end_turn":
                return self._extract_text(response)

            if response.stop_reason == "tool_use":
                # Collect tool use blocks
                tool_blocks = [b for b in response.content if b.type == "tool_use"]

                # Add assistant message with tool calls (without thinking blocks)
                messages.append({"role": "assistant", "content": clean_content})

                # Execute tools in parallel
                tool_results = await self._execute_tools_parallel(tool_blocks)
                messages.append({"role": "user", "content": tool_results})

                continue

            # stop_reason could be max_tokens, refusals, etc.
            return self._extract_text(response)

        return "Analysis did not complete within the maximum number of turns."

    async def _execute_tools_parallel(self, tool_blocks: list) -> list[dict[str, Any]]:
        """Execute multiple tool calls concurrently using asyncio.gather.

        Args:
            tool_blocks: List of tool_use content blocks from Claude.

        Returns:
            List of tool_result content blocks to send back to Claude.
        """

        async def execute_one(block) -> dict[str, Any]:
            tool_name = block.name
            tool_input = block.input if isinstance(block.input, dict) else {}

            try:
                # Import here to avoid circular imports
                from app.tools import TOOL_REGISTRY

                tool_fn = TOOL_REGISTRY.get(tool_name)
                if tool_fn is None:
                    return {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Error: Unknown tool '{tool_name}'",
                        "is_error": True,
                    }

                # Call the tool
                if asyncio.iscoroutinefunction(tool_fn):
                    result = await tool_fn(**tool_input)
                else:
                    result = await asyncio.to_thread(tool_fn, **tool_input)

                # Ensure result is a string
                if not isinstance(result, str):
                    result = json.dumps(result, indent=2, default=str)

                return {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                }
            except Exception as e:
                return {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": f"Error executing {tool_name}: {str(e)}",
                    "is_error": True,
                }

        return await asyncio.gather(*[execute_one(b) for b in tool_blocks])

    def _build_user_message(self, context: AgentContext) -> str:
        """Build the user message with full context.

        Includes the user's query, the stock symbol, and any findings
        from agents that ran earlier in the pipeline.
        """
        parts = []

        if context.symbol:
            parts.append(f"**Stock being analyzed:** {context.symbol}")

        # Include prior agent findings for context
        if context.news_sentiment:
            parts.append(
                f"\n**News Agent already found:**\n{context.news_sentiment[:2000]}"
            )
        if context.financial_summary:
            parts.append(
                f"\n**Financial Agent already found:**\n{context.financial_summary[:2000]}"
            )
        if context.market_data:
            parts.append(
                f"\n**Market Agent already found:**\n{context.market_data[:2000]}"
            )

        parts.append(f"\n**User's question:**\n{context.user_query}")
        parts.append(
            "\nRemember: Explain everything in beginner-friendly language. Define terms. Use analogies."
        )

        return "\n".join(parts)

    @staticmethod
    def _extract_text(response) -> str:
        """Extract text content from a Claude API response.

        Handles text blocks and skips thinking/redacted_thinking blocks
        (which contain model reasoning, not the actual response).
        """
        text_parts = []
        for block in response.content:
            if block.type == "text":
                text_parts.append(block.text)
            # Skip thinking, redacted_thinking, and tool_use blocks
        return "".join(text_parts)
