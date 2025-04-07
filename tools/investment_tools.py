"""Investment Tools Module.

This module provides tools for calculating investment returns and validating stock data.
"""

import sys
from pathlib import Path
from typing import Any

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


def calculate_investment_return_simple(
    input_data: InvestmentReturnInput,
) -> dict[str, Any]:
    """Calculate investment returns and annual return rate.

    Args:
    ----
        input_data (InvestmentReturnInput): Validated input data using Pydantic model.

    Returns:
    -------
        Dict[str, Any]: Investment details including final
        value, profit/loss, and returns.

    Raises:
    ------
        ValueError: If inputs are invalid
        (negative values or unreasonable annual return).

    """
    logger.info(
        f"Calculating simple investment return with "
        f"initial_amount={input_data.initial_amount}, years={input_data.years}, "
        f"annual_return={input_data.annual_return}%",
    )

    try:
        # Unpack validated inputs
        initial_amount = input_data.initial_amount
        years = input_data.years
        annual_return = input_data.annual_return

        # Convert annual return percentage to decimal
        return_rate = annual_return / 100

        # Calculate final value using compound interest formula: A = P(1 + r)^t
        final_value = initial_amount * (1 + return_rate) ** years
        profit_loss = final_value - initial_amount
        total_percentage_return = (
            (profit_loss / initial_amount) * 100 if initial_amount > 0 else 0
        )

        logger.info(
            f"Investment return calculated: final_value={final_value:.2f}, "
            f"profit/loss={profit_loss:.2f}, "
            f"return%={total_percentage_return:.2f}",
        )

        return {
            "initial_amount": round(initial_amount, 2),
            "years": years,
            "annual_return": annual_return,
            "final_value": round(final_value, 2),
            "profit_loss": round(profit_loss, 2),
            "total_percentage_return": round(total_percentage_return, 2),
        }

    except ValueError as e:
        logger.error(str(e))
        raise
    except Exception as e:
        error_message = f"Error calculating investment return: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e


