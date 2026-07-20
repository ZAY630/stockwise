"""News Analysis Agent — fetches financial news, analyzes sentiment, predicts market impact."""

from anthropic import AsyncAnthropic

from app.agents.base import BaseAgent
from app.agents.prompts import NEWS_AGENT_PROMPT
from app.agents.tool_schemas import NEWS_AGENT_TOOLS, SHARED_TOOLS


class NewsAnalysisAgent(BaseAgent):
    """Fetches and analyzes financial news with sentiment analysis.

    Shows full reasoning chains connecting news events to potential
    stock price impacts — educational for beginners learning how
    markets react to information.
    """

    name = "News Analysis Agent"
    system_prompt = NEWS_AGENT_PROMPT
    tools = NEWS_AGENT_TOOLS + SHARED_TOOLS

    def __init__(self, client: AsyncAnthropic, model: str | None = None):
        super().__init__(client, model)
