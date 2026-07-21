"""Analysis-related Pydantic schemas."""

from pydantic import BaseModel, Field


class AnalysisRequest(BaseModel):
    """Request to run an agent analysis."""

    symbol: str = Field(..., min_length=1, max_length=20, description="Stock ticker symbol")
    question: str | None = Field(None, description="Optional specific question")
    market: str | None = Field(None, description="Market code: us or cn")


class AnalysisResponse(BaseModel):
    """Response from an agent analysis."""

    symbol: str
    agent: str
    analysis: str
