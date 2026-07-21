"""Chat-related Pydantic schemas."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """A chat message request."""

    query: str = Field(..., min_length=1, description="User's question or message")
    symbol: str | None = Field(None, description="Optional stock symbol for context")
    stream: bool = Field(True, description="Whether to stream the response via SSE")
    api_key: str | None = Field(None, description="User's own Anthropic API key (never stored on server)")


class ChatMessage(BaseModel):
    """A single chat message."""

    role: str  # "user", "financial_agent", "news_agent", "market_agent", "orchestrator"
    content: str
    agent: str | None = None  # Name of the agent that sent this message
    symbol: str | None = None


class ChatResponse(BaseModel):
    """Non-streaming chat response."""

    query: str
    mode: str
    response: str
