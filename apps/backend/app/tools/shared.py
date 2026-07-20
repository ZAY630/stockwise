"""Shared tools available to all agents."""

from app.services.yfinance_service import YFinanceService


async def get_company_info(symbol: str) -> str:
    """Get basic company information: name, sector, industry, description."""
    info = await YFinanceService.get_stock_info(symbol.upper())

    return f"""Company Info for {symbol.upper()}:
Name: {info.get('longName', info.get('shortName', 'N/A'))}
Sector: {info.get('sector', 'N/A')}
Industry: {info.get('industry', 'N/A')}
Market Cap: ${info.get('marketCap', 0):,} (f"{info.get('marketCap', 0) / 1e9:.1f}B")
Employees: {info.get('fullTimeEmployees', 'N/A')}
Headquarters: {info.get('city', '')}, {info.get('state', '')}, {info.get('country', '')}
Website: {info.get('website', 'N/A')}
Business Summary: {info.get('longBusinessSummary', 'N/A')[:500]}"""
