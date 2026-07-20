"""SEC EDGAR service using edgartools library.

Fetches SEC filings (10-K, 10-Q) and parsed financial statements.
"""

from typing import Any

from app.middleware.error_handler import DataUnavailableError
from app.services.cache_service import cache


class EdgarService:
    """Wrapper around edgartools for SEC EDGAR data access."""

    @staticmethod
    async def get_financial_statements(symbol: str) -> dict[str, Any]:
        """Get standardized financial statements from the latest 10-K/10-Q filings.

        Returns income statement, balance sheet, and cash flow data.
        """
        cache_key = f"edgar_financials_{symbol}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            # edgartools is synchronous, so we run it in a thread
            import asyncio

            def _fetch():
                try:
                    from edgar import Company

                    company = Company(symbol)
                    financials = company.financials

                    result = {}
                    if financials is not None:
                        # Convert DataFrames to dicts for JSON serialization
                        for attr in [
                            "income_statement",
                            "balance_sheet",
                            "cash_flow_statement",
                        ]:
                            df = getattr(financials, attr, None)
                            if df is not None:
                                result[attr] = df.to_dict(orient="records")

                    return result if result else {"message": "No financial data available via EDGAR"}
                except ImportError:
                    return {
                        "message": "edgartools not installed. Install with: pip install edgartools"
                    }
                except Exception as e:
                    return {"error": str(e)}

            result = await asyncio.to_thread(_fetch)
            if "error" not in result:
                await cache.set(cache_key, result, ttl_seconds=3600)  # 1 hour TTL
            return result
        except Exception as e:
            raise DataUnavailableError(f"Failed to fetch SEC filings for {symbol}: {str(e)}")

    @staticmethod
    async def get_latest_filing(
        symbol: str, filing_type: str = "10-K"
    ) -> dict[str, Any]:
        """Get the latest SEC filing of a specific type."""
        cache_key = f"edgar_filing_{symbol}_{filing_type}"
        cached = await cache.get(cache_key)
        if cached:
            return cached

        try:
            import asyncio

            def _fetch():
                try:
                    from edgar import Company

                    company = Company(symbol)
                    filings = company.get_filings(form=filing_type).latest(1)

                    if filings is not None and not filings.empty:
                        filing = filings.iloc[0]
                        return {
                            "filing_type": filing_type,
                            "filing_date": str(filing.get("filing_date", "")),
                            "report_date": str(filing.get("report_date", "")),
                            "accession_number": str(filing.get("accession_number", "")),
                        }
                    return {"message": f"No {filing_type} filings found"}
                except ImportError:
                    return {"message": "edgartools not installed"}
                except Exception as e:
                    return {"error": str(e)}

            result = await asyncio.to_thread(_fetch)
            if "error" not in result:
                await cache.set(cache_key, result, ttl_seconds=3600)
            return result
        except Exception as e:
            raise DataUnavailableError(f"Failed to fetch {filing_type} for {symbol}: {str(e)}")
