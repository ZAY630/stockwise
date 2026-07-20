"""Agent analysis endpoints."""

from fastapi import APIRouter, HTTPException

from app.agents.orchestrator import OrchestrationMode, get_orchestrator
from app.schemas.analysis import AnalysisRequest, AnalysisResponse

router = APIRouter()


@router.post("/financial", response_model=AnalysisResponse)
async def analyze_financials(request: AnalysisRequest):
    """Run the Financial Report Agent on a stock."""
    try:
        orchestrator = await get_orchestrator()
        result = await orchestrator.route_and_execute(
            query=f"Analyze the financial health of {request.symbol}. {request.question or ''}",
            symbol=request.symbol.upper(),
            mode=OrchestrationMode.SINGLE,
            force_agent="financial",
        )
        return AnalysisResponse(
            symbol=request.symbol.upper(),
            agent="Financial Report Agent",
            analysis=result["result"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/news", response_model=AnalysisResponse)
async def analyze_news(request: AnalysisRequest):
    """Run the News Analysis Agent on a stock."""
    try:
        orchestrator = await get_orchestrator()
        result = await orchestrator.route_and_execute(
            query=f"Analyze recent news and sentiment for {request.symbol}. {request.question or ''}",
            symbol=request.symbol.upper(),
            mode=OrchestrationMode.SINGLE,
            force_agent="news",
        )
        return AnalysisResponse(
            symbol=request.symbol.upper(),
            agent="News Analysis Agent",
            analysis=result["result"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/market", response_model=AnalysisResponse)
async def analyze_market(request: AnalysisRequest):
    """Run the Market Data Agent on a stock."""
    try:
        orchestrator = await get_orchestrator()
        result = await orchestrator.route_and_execute(
            query=f"Analyze the market data and technical indicators for {request.symbol}. {request.question or ''}",
            symbol=request.symbol.upper(),
            mode=OrchestrationMode.SINGLE,
            force_agent="market",
        )
        return AnalysisResponse(
            symbol=request.symbol.upper(),
            agent="Market Data Agent",
            analysis=result["result"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/comprehensive", response_model=AnalysisResponse)
async def analyze_comprehensive(request: AnalysisRequest):
    """Run all three agents and synthesize a comprehensive analysis."""
    try:
        orchestrator = await get_orchestrator()
        result = await orchestrator.route_and_execute(
            query=request.question or f"Give me a comprehensive analysis of {request.symbol}. Should I invest?",
            symbol=request.symbol.upper(),
            mode=OrchestrationMode.SEQUENTIAL,
        )
        return AnalysisResponse(
            symbol=request.symbol.upper(),
            agent="StockWise Orchestrator (All Agents)",
            analysis=result.get("synthesis", str(result)),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
