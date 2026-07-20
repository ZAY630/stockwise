"""Financial Report Agent — analyzes company financials, SEC filings, and key ratios."""

from anthropic import AsyncAnthropic

from app.agents.base import BaseAgent
from app.agents.prompts import FINANCIAL_AGENT_PROMPT
from app.agents.tool_schemas import FINANCIAL_AGENT_TOOLS, SHARED_TOOLS


class FinancialReportAgent(BaseAgent):
    """Analyzes company financial reports, SEC filings, and key ratios.

    Explains financial metrics in plain English with analogies —
    designed for beginners learning to read financial statements.
    """

    name = "Financial Report Agent"
    system_prompt = FINANCIAL_AGENT_PROMPT
    tools = FINANCIAL_AGENT_TOOLS + SHARED_TOOLS

    def __init__(self, client: AsyncAnthropic, model: str | None = None):
        super().__init__(client, model)
