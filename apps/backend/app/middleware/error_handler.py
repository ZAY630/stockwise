"""Global exception handlers."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class StockWiseError(Exception):
    """Base exception for StockWise application."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code


class DataUnavailableError(StockWiseError):
    """Raised when external data cannot be fetched."""

    def __init__(self, message: str = "Data temporarily unavailable"):
        super().__init__(message, status_code=503)


class InvalidSymbolError(StockWiseError):
    """Raised when an invalid stock symbol is provided."""

    def __init__(self, symbol: str):
        super().__init__(
            f"Invalid stock symbol: '{symbol}'. Please check the ticker and try again.",
            status_code=404,
        )


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the app."""

    @app.exception_handler(StockWiseError)
    async def stockwise_error_handler(request: Request, exc: StockWiseError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "type": type(exc).__name__},
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=400,
            content={"error": str(exc), "type": "ValueError"},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "An unexpected error occurred", "type": "InternalError"},
        )
