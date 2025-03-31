"""Investment Tools Module.

This module provides tools for calculating investment returns and validating stock data.
"""
import sys
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf
from loguru import logger

# Add project root to sys.path for module imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_setup import setup_logging
from utils.models import InvestmentReturnInput

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"

# Set up logging at module level
logging_configs = setup_logging(str(DEFAULT_CONFIG_PATH))
logger.info("Logging initialized for Investment_tools.py")


def validate_data(
    data: pd.DataFrame,
    symbol: str,
    start_date: str,
    end_date: str,
) -> None:
    """Validate if the data is not empty and raise an error if it is.

    Args:
        data: Data to validate (e.g., stock history).
        symbol: Stock ticker symbol.
        start_date: Start date for historical data.
        end_date: End date for historical data.

    Raises:
        ValueError: If the data is empty.

    """
    if data.empty:
        error_message = (
            f"No historical data for {symbol} between "
            f"{start_date} and {end_date}"
        )
        logger.error(error_message)
        raise ValueError(error_message)

# 3. Investment Calculator
def calculate_investment_return(input_data: InvestmentReturnInput) -> dict[str, Any]:
    """Calculate investment returns for a given stock.

    Args:
        input_data (InvestmentReturnInput): Validated input data using Pydantic.

    Returns:
        Dict[str, Any]: Investment details including profit/loss and percentage return.

    """
    logger.info(
        f"Calculating investment return for {input_data.symbol} "
        f"from {input_data.start_date} to {input_data.end_date}",
    )

    try:
        # Fetch stock data
        stock = yf.Ticker(input_data.symbol)
        hist = stock.history(start=input_data.start_date, end=input_data.end_date)

        # Validate historical data
        validate_data(hist,input_data.symbol,input_data.start_date,input_data.end_date)

        # Calculate investment metrics
        start_price = hist["Close"].iloc[0]
        end_price = hist["Close"].iloc[-1]
        shares = input_data.initial_amount / start_price
        final_value = shares * end_price
        profit_loss = final_value - input_data.initial_amount
        percentage_return = (profit_loss / input_data.initial_amount) * 100

        logger.info(
            f"Investment return calculated: profit/loss={profit_loss:.2f}, "
            f"return%={percentage_return:.2f}",
        )

        return {
            "symbol": input_data.symbol,
            "initial_amount": input_data.initial_amount,
            "start_date": input_data.start_date,
            "end_date": input_data.end_date,
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
        error_message = f"""Error calculating investment return
                   for {input_data.symbol}: {e}"""
        logger.error(error_message)
        raise ValueError(error_message) from e
