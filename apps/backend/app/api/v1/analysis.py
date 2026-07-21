"""Agent analysis endpoints."""

from fastapi import APIRouter, HTTPException

from app.agents.orchestrator import OrchestrationMode, get_orchestrator
from app.market_config import get_market
from app.schemas.analysis import AnalysisRequest, AnalysisResponse


async def _get_orch(api_key: str | None):
    """Get orchestrator with user's API key. None = use server key."""
    return await get_orchestrator(api_key)

router = APIRouter()

# Agent name translations per market
AGENT_LABELS = {
    "us": {
        "financial": "Financial Report Agent",
        "news": "News Analysis Agent",
        "market": "Market Data Agent",
        "orchestrator": "StockWise Orchestrator (All Agents)",
    },
    "cn": {
        "financial": "财务分析智能体",
        "news": "新闻分析智能体",
        "market": "市场数据智能体",
        "orchestrator": "StockWise 综合分析 (全部智能体)",
    },
}


def _make_query(base_query: str, market_code: str | None) -> str:
    """Append market language instruction to the query."""
    mkt = get_market(market_code)
    return f"{mkt.language_instruction}\n\n{base_query}"


def _labels(market_code: str | None):
    return AGENT_LABELS.get(market_code or "us", AGENT_LABELS["us"])


@router.post("/financial", response_model=AnalysisResponse)
async def analyze_financials(request: AnalysisRequest):
    """Run the Financial Report Agent on a stock."""
    try:
        orchestrator = await _get_orch(request.api_key)
        result = await orchestrator.route_and_execute(
            query=_make_query(
                f"Analyze the financial health of {request.symbol}. {request.question or ''}",
                request.market,
            ),
            symbol=request.symbol.upper(),
            mode=OrchestrationMode.SINGLE,
            force_agent="financial",
        )
        return AnalysisResponse(
            symbol=request.symbol.upper(),
            agent=_labels(request.market)["financial"],
            analysis=result["result"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/news", response_model=AnalysisResponse)
async def analyze_news(request: AnalysisRequest):
    """Run the News Analysis Agent on a stock."""
    try:
        orchestrator = await _get_orch(request.api_key)
        result = await orchestrator.route_and_execute(
            query=_make_query(
                f"Analyze recent news and sentiment for {request.symbol}. {request.question or ''}",
                request.market,
            ),
            symbol=request.symbol.upper(),
            mode=OrchestrationMode.SINGLE,
            force_agent="news",
        )
        return AnalysisResponse(
            symbol=request.symbol.upper(),
            agent=_labels(request.market)["news"],
            analysis=result["result"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/market", response_model=AnalysisResponse)
async def analyze_market(request: AnalysisRequest):
    """Run the Market Data Agent on a stock."""
    try:
        orchestrator = await _get_orch(request.api_key)
        result = await orchestrator.route_and_execute(
            query=_make_query(
                f"Analyze the market data and technical indicators for {request.symbol}. {request.question or ''}",
                request.market,
            ),
            symbol=request.symbol.upper(),
            mode=OrchestrationMode.SINGLE,
            force_agent="market",
        )
        return AnalysisResponse(
            symbol=request.symbol.upper(),
            agent=_labels(request.market)["market"],
            analysis=result["result"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/comprehensive", response_model=AnalysisResponse)
async def analyze_comprehensive(request: AnalysisRequest):
    """Run all three agents in parallel and synthesize a comprehensive analysis."""
    try:
        orchestrator = await _get_orch(request.api_key)
        result = await orchestrator.route_and_execute(
            query=_make_query(
                request.question or f"Give me a comprehensive analysis of {request.symbol}. Should I invest?",
                request.market,
            ),
            symbol=request.symbol.upper(),
            mode=OrchestrationMode.PARALLEL,
        )
        return AnalysisResponse(
            symbol=request.symbol.upper(),
            agent=_labels(request.market)["orchestrator"],
            analysis=result.get("synthesis", str(result)),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
