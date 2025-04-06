"""Stock Price Checker Tool."""
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf
from loguru import logger

# Add project root to sys.path for module imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_setup import setup_logging
from utils.models import StockPriceInput

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"

# Set up logging at module level
logging_configs = setup_logging(str(DEFAULT_CONFIG_PATH))
logger.info("Logging initialized for stock_tools.py")


def validate_data(
    data: pd.DataFrame,
    symbol: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> None:
    """Validate if the data is not empty and raise an error if it is.

    Args:
        data: Data to validate (e.g., stock history).
        symbol: Stock ticker symbol.
        start_date: Start date for historical data (optional).
        end_date: End date for historical data (optional).

    Raises:
        ValueError: If the data is empty.

    """
    error_message = None
    if data.empty:
        if start_date and end_date:
            error_message = (
                f"No historical data for {symbol} between "
                f"{start_date} and {end_date}"
            )
        else:
            error_message = f"No current data available for {symbol}"

    if error_message:
        logger.error(error_message)
        raise ValueError(error_message)


def get_stock_prices(input_data: StockPriceInput) -> dict[str, Any]:
    """Retrieve current and historical stock prices.

    Args:
        input_data (StockPriceInput): Validated input data using Pydantic.

    Returns:
        dict[str, Any]: Current price and historical prices if requested.

    """
    logger.info(f"Fetching stock prices for {input_data.symbol}")
    try:
        stock = yf.Ticker(input_data.symbol)

        # Fetch current data
        current_data = stock.history(period="1d")
        validate_data(current_data, input_data.symbol)

        current_price = current_data["Close"].iloc[-1]

        # Fetch historical data if dates are provided
        historical_data = None
        if input_data.start_date and input_data.end_date:
            hist = stock.history(start=input_data.start_date, end=input_data.end_date)
            validate_data(hist, input_data.symbol, input_data.start_date,
                          input_data.end_date)
            historical_data = hist["Close"].to_dict()

        logger.info(f"Successfully fetched stock prices for {input_data.symbol}")
        return {
            "symbol": input_data.symbol,
            "current_price": float(current_price),
            "historical_data": historical_data,
        }

    except ValueError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        error_message = f"Error fetching stock prices for {input_data.symbol}: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e

