"""Spending analysis tools."""
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
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
logger.info("Logging initialized for spending_tools.py")


def get_spending_breakdown(
    data_source: str | None = None,
    year: str = "2023",
    *,
    use_bea: bool = True,  # Make `use_bea` keyword-only
) -> dict[str, Any]:
    """Generate a spending breakdown and create a pie chart.

    Args:
        data_source: Optional path to a CSV file.
        year: Year for BEA data (default: 2023).
        use_bea: If True, fetch from BEA API; otherwise, use simulator.

    Returns:
        dict: Spending breakdown by category and path to the saved chart.

    """
    logger.info(f"Generating spending breakdown for year {year}")
    try:
        # Determine data source
        if data_source:
            spending_df = pd.read_csv(data_source)
            source = "csv"
        elif use_bea:
            spending_df = get_bea_spending_data(year)
            # Scale from millions to a personal estimate
            spending_df["amount"] = spending_df["amount"] / 1000 #Adjust scaling
            source = "bea_api"
        elif DATA_PATH.exists():
            spending_df = (
                pd.read_csv(DATA_PATH)
                .groupby("category")["amount"]
                .sum()
                .reset_index()
            )
            source = "csv"
        else:
            spending_df = generate_spending_data()
            source = "simulated"

        # Validate DataFrame columns
        required_columns = {"category", "amount"}
        if not required_columns.issubset(spending_df.columns):
            error_message = "Spending data must contain 'category' and 'amount' columns"
            raise ValueError(error_message)

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
            f"Spending Breakdown ({year}, Source: {source.capitalize()})", wrap=True,
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

    except OSError as e:  # Catch specific exceptions instead of a blind `Exception`
        error_message = f"Error generating spending breakdown: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e


if __name__ == "__main__":
    result = get_spending_breakdown()
