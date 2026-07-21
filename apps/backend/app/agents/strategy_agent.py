"""Trading Strategy Agent — actionable buy/sell/position advice.

This agent synthesizes analysis from the Financial, News, and Market agents
to produce concrete trading plans with specific price levels.
"""

from anthropic import AsyncAnthropic

from app.agents.base import BaseAgent, AgentContext
from app.agents.prompts import STRATEGY_AGENT_PROMPT


class StrategyAgent(BaseAgent):
    """Provides actionable trading strategies based on multi-agent analysis.

    Takes the output of financial, news, and market analysis as input
    and produces specific entry/exit prices, position sizing, and risk management.
    """

    name = "Trading Strategy Agent"
    system_prompt = STRATEGY_AGENT_PROMPT
    tools = []  # No tools — this agent synthesizes, doesn't fetch data

    def __init__(self, client: AsyncAnthropic, model: str | None = None):
        super().__init__(client, model)

    async def analyze(self, context: AgentContext) -> str:
        """Generate a trading strategy based on the other agents' analysis.

        Expects context to have financial_summary, news_sentiment, and market_data
        populated by the other agents.
        """
        return await super().analyze(context)
