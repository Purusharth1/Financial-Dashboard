"""Cryptocurrency Tracker Tool."""
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import requests
from loguru import logger

# Add project root to sys.path for module imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_setup import setup_logging
from utils.models import CryptoInput  # Import the Pydantic model

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"

# Set up logging at module level
logging_configs = setup_logging(str(DEFAULT_CONFIG_PATH))
logger.info("Logging initialized for crypto_tools.py")


def get_historical_price(crypto_id: str, date: str, vs_currency: str = "usd") -> float:
    """Retrieve historical cryptocurrency price for a specific date using CryptoCompare.

    Args:
        crypto_id: Cryptocurrency ID (e.g., 'BTC').
        date: Date in 'YYYY-MM-DD' format.
        vs_currency: Currency to compare against (e.g., 'usd', default: 'usd').

    Returns:
        float: Historical price of the cryptocurrency on the given date.

    Raises:
        ValueError: If no historical data is found for the given date.

    """
    try:
        # Convert date to timestamp with timezone awareness
        dt = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=UTC)
        timestamp = int(dt.timestamp())

        url = f"https://min-api.cryptocompare.com/data/pricehistorical?fsym={crypto_id}&tsyms={vs_currency.upper()}&ts={timestamp}"
        logger.info(f"Fetching historical price for {crypto_id} on {date}")

        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Validate data and raise error if missing
        if crypto_id not in data or vs_currency.upper() not in data[crypto_id]:
            error_message = f"No historical data found for {crypto_id} on {date}"
            logger.error(error_message)
            raise ValueError(error_message)

        return data[crypto_id][vs_currency.upper()]

    except requests.RequestException as e:
        error_message = f"Error fetching historical data for {crypto_id} on {date}: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e


def get_crypto_data(input_data: CryptoInput) -> dict[str, Any]:
    """Retrieve current cryptocurrency data and calculate price increase b/w two dates.

    Args:
        input_data: Validated input data using Pydantic.

    Returns:
        Dict[str, Any]: Current price, 24-hour price change,
           and price increase between dates (if provided).

    Raises:
        ValueError: If inputs are invalid or no data is available.

    """
    logger.info(
        f"Fetching crypto data for {input_data.crypto_id} in {input_data.vs_currency}",
    )

    try:
        # Fetch current data
        url = (
            f"https://min-api.cryptocompare.com/data/price?"
            f"fsym={input_data.crypto_id}&tsyms={input_data.vs_currency.upper()}"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Validate data and raise error if missing
        if input_data.vs_currency.upper() not in data:
            error_message = f"No data found for cryptocurrency {input_data.crypto_id}"
            logger.error(error_message)
            raise ValueError(error_message)

        current_price = data[input_data.vs_currency.upper()]

        # Initialize result dictionary
        result = {
            "crypto_id": input_data.crypto_id,
            "vs_currency": input_data.vs_currency,
            "current_price": current_price,
        }

        # Calculate price increase between two dates if provided
        if input_data.start_date and input_data.end_date:
            start_price = get_historical_price(
                input_data.crypto_id, input_data.start_date, input_data.vs_currency,
            )
            end_price = get_historical_price(
                input_data.crypto_id, input_data.end_date, input_data.vs_currency,
            )

            # Calculate percentage increase
            price_increase_percentage = (
                ((end_price - start_price) /start_price) * 100 if start_price > 0 else 0
            )

            # Add historical data to result
            result.update(
                {
                    "start_date": input_data.start_date,
                    "end_date": input_data.end_date,
                    "start_price": start_price,
                    "end_price": end_price,
                    "price_increase_percentage": round(price_increase_percentage, 2),
                },
            )

        logger.info(
            f"Successfully fetched crypto data for {input_data.crypto_id}. "
            f"Target fund size calculated.",
        )

    except requests.RequestException as e:
        error_message = f"Error fetching crypto data for {input_data.crypto_id}: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e

    else:
        return result

