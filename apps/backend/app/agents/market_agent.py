"""Market Data Agent — analyzes price data, technical indicators, and trends."""

from anthropic import AsyncAnthropic

from app.agents.base import BaseAgent
from app.agents.prompts import MARKET_AGENT_PROMPT
from app.agents.tool_schemas import MARKET_AGENT_TOOLS, SHARED_TOOLS


class MarketDataAgent(BaseAgent):
    """Analyzes stock prices, technical indicators, and market trends.

    Generates buy/sell/hold recommendations with educational explanations.
    """

    name = "Market Data Agent"
    system_prompt = MARKET_AGENT_PROMPT
    tools = MARKET_AGENT_TOOLS + SHARED_TOOLS

    def __init__(self, client: AsyncAnthropic, model: str | None = None):
        super().__init__(client, model)
