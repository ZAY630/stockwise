"""Common/shared Pydantic schemas."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str
    type: str


class HealthCheck(BaseModel):
    """Health check response."""

    status: str
    version: str
