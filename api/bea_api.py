"""BEA API integration for economic data."""
import sys
from pathlib import Path
from typing import NoReturn

import pandas as pd
import requests
from loguru import logger

# Add project root to sys.path for module imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.configs import load_config
from utils.logging_setup import setup_logging

# Define project root relative to this file (api/)
PROJECT_ROOT = Path(__file__).parent.parent  # financial_dashboard/
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"

# Set up logging at module level
logging_configs = setup_logging(str(DEFAULT_CONFIG_PATH))
logger.info("Logging initialized for bea_api.py")

# Load BEA configuration
config = load_config()
BEA_API_KEY = config["api"]["bea_api_key"]


def get_bea_spending_data(year: str = "2023") -> pd.DataFrame:
    """Fetch personal consumption expenditures (PCE) data from BEA API.

    Args:
        year: Year to fetch data for (default: 2023).

    Returns:
        pd.DataFrame: Spending data with 'category' and 'amount' columns.

    """
    logger.info(f"Fetching BEA spending data for year {year}")
    url = (
        "https://apps.bea.gov/api/data/"
        f"?UserID={BEA_API_KEY}"
        "&method=GetData"
        "&datasetname=NIPA"
        "&TableName=T20305"  # PCE by major type of product, quarterly
        "&Frequency=Q"  # Quarterly data
        f"&Year={year}"
        "&ResultFormat=JSON"
    )

    def raise_no_data_error(message: str) -> NoReturn:
        """Log and raise an error for missing data."""
        logger.error(message)
        raise ValueError(message)

    try:
        # Use a timeout for the requests call to avoid hanging
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Log the raw response for debugging
        logger.debug(f"BEA API response: {data}")

        # Extract data from response
        results = data["BEAAPI"]["Results"]["Data"]

        if not results:
            error_message = "No data returned from BEA API"
            logger.error(error_message)
            raise_no_data_error(error_message)

        # Updated category mapping based on actual T20305 SeriesCode values
        category_map = {
            "DFXARC": "Food", #Food and beverages purchased for off-premises consumption
            "DHUTRC": "Housing",  # Housing and utilities
            "DTRSRC": "Transportation",  # Transportation services
            "DRCARC": "Entertainment",  # Recreation services
            "DCLORC": "Shopping",  # Clothing and footwear
            "DHLCRC": "Health Care",  # Health care
        }

        spending_data = []
        for item in results:
            series_code = item["SeriesCode"]
            if series_code in category_map:
                # Convert DataValue to float, removing commas
                amount = float(item["DataValue"].replace(",", ""))
                spending_data.append(
                    {
                        "category": category_map[series_code],
                        "amount": amount,
                        "quarter": item["TimePeriod"],  # Include quarter for reference
                    },
                )

        if not spending_data:
            categories = list(category_map.keys())
            error_message = (
                f"No matching spending data found for categories: {categories}"
            )
            logger.error(error_message)
            raise_no_data_error(error_message)

        # Create DataFrame and aggregate across quarters
        spending_df = pd.DataFrame(spending_data)
        spending_agg_df = (
            spending_df.groupby("category")["amount"].sum().reset_index()
        )

        # Log aggregated data
        log_message = (
            f"Retrieved and aggregated BEA spending data: {spending_agg_df.to_dict()}"
        )
        logger.info(log_message)

    except requests.RequestException as e:
        error_message = f"Error fetching BEA data: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e

    except Exception as e:
        error_message = f"Error processing BEA data: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e

    else:
        return spending_agg_df



