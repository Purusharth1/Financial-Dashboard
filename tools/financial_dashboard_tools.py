"""Financial Dashboard Tools.

This module contains functions for analyzing stock data, calculating investment returns,
checking cryptocurrency prices, visualizing spending patterns, providing financial advice,
and performing multi-asset analysis.
"""

# change function 1 for csv
# change function 2 to get price of the specific date
# change function 4 to get return percentage for a custom period
# check if the till which date api is giving result. and mention here
# correct ruff and check logging
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import requests
import yfinance as yf
from loguru import logger

# Add project root to sys.path for module imports
sys.path.append(str(Path(__file__).parent.parent))
from api.bea_api import get_bea_spending_data
from data.data_simulator import generate_spending_data
from utils.logging_setup import setup_logging

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "spending_data.csv"
CHART_PATH = PROJECT_ROOT / "ui" / "assets" / "spending_breakdown.png"
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"

# Set up logging at module level
logging_configs = setup_logging(str(DEFAULT_CONFIG_PATH))
logger.info("Logging initialized for financial_dashboard_tools.py")


# 1. Spending Breakdown Tool (Provided)
def get_spending_breakdown(
    data_source: str | None = None,
    year: str = "2023",
    *,
    use_bea: bool = True,
) -> dict[str, Any]:
    """Generate a spending breakdown and create a pie chart.

    Args:
    ----
        data_source: Optional path to a CSV file.
        year: Year for BEA data (default: '2023').
        use_bea: If True, fetch from BEA API; otherwise, use simulator.

    Returns:
    -------
        Dict[str, Any]: Spending breakdown by category and path to the saved chart.

    """
    logger.info(f"Generating spending breakdown for year {year}")
    try:
        # Determine data source
        if data_source:
            spending_df = pd.read_csv(data_source)
            source = "csv"
        elif use_bea:
            spending_df = get_bea_spending_data(year)
            spending_df["amount"] = spending_df["amount"] / 1000  # Scale from millions
            source = "bea_api"
        elif DATA_PATH.exists():
            spending_df = (
                pd.read_csv(DATA_PATH).groupby("category")["amount"].sum().reset_index()
            )
            source = "csv"
        else:
            spending_df = generate_spending_data()
            source = "simulated"

        # Validate DataFrame columns
        required_columns = {"category", "amount"}
        if not required_columns.issubset(spending_df.columns):
            raise ValueError(
                "Spending data must contain 'category' and 'amount' columns",
            )

        # Generate breakdown
        breakdown = spending_df.groupby("category")["amount"].sum().to_dict()
        total_spent = sum(breakdown.values())

        # Create pie chart
        plt.figure(figsize=(8, 8))
        plt.pie(
            breakdown.values(),
            labels=breakdown.keys(),
            autopct="%1.1f%%",
            startangle=90,
        )
        plt.title(
            f"Spending Breakdown ({year}, Source: {source.capitalize()})",
            wrap=True,
        )
        plt.axis("equal")
        plt.savefig(CHART_PATH, bbox_inches="tight")
        plt.close()

        logger.info(f"Spending breakdown: {breakdown}, chart saved to {CHART_PATH}")
        return {
            "breakdown": breakdown,
            "total_spent": total_spent,
            "chart_path": str(CHART_PATH),
            "source": source,
        }
    except OSError as e:
        error_message = f"Error generating spending breakdown: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e


# 2. Stock Price Checker
def get_stock_prices(
    symbol: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict[str, Any]:
    """Retrieve current and historical stock prices.

    Args:
    ----
        symbol: Stock ticker symbol (e.g., 'AAPL').
        start_date: Start date for historical data (format: 'YYYY-MM-DD'), optional.
        end_date: End date for historical data (format: 'YYYY-MM-DD'), optional.

    Returns:
    -------
        Dict[str, Any]: Current price and historical prices if requested.

    """
    logger.info(f"Fetching stock prices for {symbol}")
    try:
        stock = yf.Ticker(symbol)
        current_data = stock.history(period="1d")
        if current_data.empty:
            raise ValueError(f"No current data available for {symbol}")
        current_price = current_data["Close"].iloc[-1]
        historical_data = None
        if start_date and end_date:
            hist = stock.history(start=start_date, end=end_date)
            if hist.empty:
                raise ValueError(
                    f"No historical data for {symbol} between {start_date} and {end_date}",
                )
            historical_data = hist["Close"].to_dict()
        logger.info(f"Successfully fetched stock prices for {symbol}")
        return {
            "symbol": symbol,
            "current_price": float(current_price),
            "historical_data": historical_data,
        }
    except ValueError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        error_message = f"Error fetching stock prices for {symbol}: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e


# 3. Investment Calculator
def calculate_investment_return(
    symbol: str,
    initial_amount: float,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """Calculate investment returns for a given stock.

    Args:
    ----
        symbol: Stock ticker symbol (e.g., 'AAPL').
        initial_amount: Initial investment amount.
        start_date: Start date of investment (format: 'YYYY-MM-DD').
        end_date: End date of investment (format: 'YYYY-MM-DD').

    Returns:
    -------
        Dict[str, Any]: Investment details including profit/loss and percentage return.

    """
    logger.info(
        f"Calculating investment return for {symbol} from {start_date} to {end_date}",
    )
    try:
        if initial_amount <= 0:
            raise ValueError("Initial amount must be positive")
        stock = yf.Ticker(symbol)
        hist = stock.history(start=start_date, end=end_date)
        if hist.empty:
            raise ValueError(
                f"No historical data for {symbol} between {start_date} and {end_date}",
            )
        start_price = hist["Close"].iloc[0]
        end_price = hist["Close"].iloc[-1]
        shares = initial_amount / start_price
        final_value = shares * end_price
        profit_loss = final_value - initial_amount
        percentage_return = (profit_loss / initial_amount) * 100
        logger.info(
            f"Investment return calculated: profit/loss={profit_loss:.2f}, return%={percentage_return:.2f}",
        )
        return {
            "symbol": symbol,
            "initial_amount": initial_amount,
            "start_date": start_date,
            "end_date": end_date,
            "start_price": float(start_price),
            "end_price": float(end_price),
            "shares": shares,
            "final_value": final_value,
            "profit_loss": profit_loss,
            "percentage_return": percentage_return,
        }
    except ValueError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        error_message = f"Error calculating investment return for {symbol}: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e


# 4. Crypto Tracker
def get_crypto_data(crypto_id: str, vs_currency: str = "usd") -> dict[str, Any]:
    """Retrieve current cryptocurrency data.

    Args:
    ----
        crypto_id: Cryptocurrency ID (e.g., 'bitcoin').
        vs_currency: Currency to compare against (e.g., 'usd', default: 'usd').

    Returns:
    -------
        Dict[str, Any]: Current price and 24-hour price change percentage.

    """
    logger.info(f"Fetching crypto data for {crypto_id} in {vs_currency}")
    try:
        url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency={vs_currency}&ids={crypto_id}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise ValueError(f"No data found for cryptocurrency {crypto_id}")
        crypto_data = data[0]
        current_price = crypto_data["current_price"]
        price_change_24h = crypto_data["price_change_percentage_24h"]
        logger.info(f"Successfully fetched crypto data for {crypto_id}")
        return {
            "crypto_id": crypto_id,
            "vs_currency": vs_currency,
            "current_price": current_price,
            "price_change_24h": price_change_24h,
        }
    except requests.RequestException as e:
        error_message = f"Error fetching crypto data for {crypto_id}: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e
    except (IndexError, KeyError) as e:
        error_message = f"Error parsing crypto data for {crypto_id}: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e


# 5. Financial Advice Tool
def get_financial_advice(portfolio: dict[str, float]) -> dict[str, Any]:
    """Provide basic financial advice based on portfolio composition.

    Args:
    ----
        portfolio: Dictionary of stock symbols and their weights (must sum to 1).

    Returns:
    -------
        Dict[str, Any]: Portfolio analysis and diversification suggestions.

    """
    logger.info("Analyzing portfolio for financial advice")
    try:
        total_weight = sum(portfolio.values())
        if not 0.99 <= total_weight <= 1.01:  # Allow small floating-point errors
            raise ValueError(f"Portfolio weights must sum to 1, got {total_weight}")

        # Get sector information
        sectors: dict[str, str] = {}
        for symbol in portfolio:
            stock = yf.Ticker(symbol)
            info = stock.info
            sectors[symbol] = info.get("sector", "Unknown")

        # Calculate sector weights
        sector_weights: dict[str, float] = {}
        for symbol, weight in portfolio.items():
            sector = sectors[symbol]
            sector_weights[sector] = sector_weights.get(sector, 0) + weight

        # Generate suggestions
        max_stock_weight = max(portfolio.values())
        max_sector_weight = max(sector_weights.values())
        suggestions = []
        if len(portfolio) < 5:
            suggestions.append(
                "Consider adding more stocks to diversify your portfolio.",
            )
        if max_stock_weight > 0.5:
            suggestions.append(
                f"No single stock should exceed 50% weight. Currently, one stock has {max_stock_weight*100:.2f}%.",
            )
        if max_sector_weight > 0.6:
            suggestions.append(
                f"No single sector should exceed 60% weight. Currently, one sector has {max_sector_weight*100:.2f}%.",
            )

        logger.info("Financial advice generated successfully")
        return {
            "portfolio": portfolio,
            "sector_weights": sector_weights,
            "suggestions": suggestions
            if suggestions
            else ["Your portfolio looks well-diversified."],
        }
    except ValueError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        error_message = f"Error generating financial advice: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e


# 6. Multi-Tool Analysis System
def analyze_multiple_assets(
    assets: list[dict[str, str]],
    initial_amount: float,
    days: int,
) -> dict[str, Any]:
    """Analyze investment returns for multiple assets over a given period.

    Args:
    ----
        assets: List of dictionaries, each with 'type' ('stock' or 'crypto') and 'id'.
        initial_amount: Initial investment amount per asset.
        days: Number of days for the investment period.

    Returns:
    -------
        Dict[str, Any]: Returns for each asset and the best performer.

    """
    logger.info(f"Analyzing multiple assets: {assets} over {days} days")
    try:
        if initial_amount <= 0:
            raise ValueError("Initial amount must be positive")
        if days <= 0:
            raise ValueError("Days must be positive")
        results: dict[str, dict[str, Any]] = {}
        for asset in assets:
            asset_type = asset["type"]
            asset_id = asset["id"]
            if asset_type == "stock":
                stock_data = yf.Ticker(asset_id).history(period=f"{days}d")
                if stock_data.empty:
                    raise ValueError(f"No data for stock {asset_id}")
                start_price = stock_data["Close"].iloc[0]
                end_price = stock_data["Close"].iloc[-1]
            elif asset_type == "crypto":
                url = f"https://api.coingecko.com/api/v3/coins/{asset_id}/market_chart?vs_currency=usd&days={days}"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                data = response.json()
                prices = data["prices"]
                if not prices:
                    raise ValueError(f"No data for crypto {asset_id}")
                start_price = prices[0][1]  # Price at earliest timestamp
                end_price = prices[-1][1]  # Price at latest timestamp
            else:
                raise ValueError(f"Invalid asset type: {asset_type}")
            shares = initial_amount / start_price
            final_value = shares * end_price
            return_percentage = (final_value - initial_amount) / initial_amount * 100
            results[asset_id] = {
                "type": asset_type,
                "return_percentage": return_percentage,
            }

        best_asset = max(results, key=lambda k: results[k]["return_percentage"])
        logger.info(f"Analysis completed: best asset is {best_asset}")
        return {"assets": results, "best_asset": best_asset}
    except (ValueError, requests.RequestException) as e:
        logger.error(str(e))
        raise
    except Exception as e:
        error_message = f"Error analyzing multiple assets: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e
