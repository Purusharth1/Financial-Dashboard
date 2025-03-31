"""Spending analysis tools."""
import sys
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from langchain_core.tools import tool
from loguru import logger

# Add project root to sys.path for module imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_setup import setup_logging
from utils.models import SpendingBreakdownInput  # Import the Pydantic model

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
CHART_PATH = PROJECT_ROOT / "ui" / "assets" / "spending_breakdown.png"
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"

# Set up logging at module level
logging_configs = setup_logging(str(DEFAULT_CONFIG_PATH))
logger.info("Logging initialized for spending_tools.py")

@tool
def get_spending_breakdown(input_data: SpendingBreakdownInput) -> dict[str, Any]:
    """Generate a spending breakdown and create a pie chart.

    Args:
        input_data: Validated input data using Pydantic.

    Returns:
        dict: Spending breakdown by category and path to the saved chart.

    Raises:
        ValueError: If the data is invalid or cannot be processed.

    """
    logger.info("Generating spending breakdown")
    try:
        # Load spending data
        if input_data.data_source:
            # Load data from CSV file
            spending_df = pd.read_csv(input_data.data_source)
            source = "csv"
        elif input_data.spending_data:
            # Convert dictionary to DataFrame
            spending_df = pd.DataFrame(
                list(input_data.spending_data.items()), columns=["category", "amount"],
            )
            source = "direct_input"

        # Validate DataFrame columns
        required_columns = {"category", "amount"}
        if not required_columns.issubset(spending_df.columns):
            error_message = "Spending data must contain 'category' and 'amount' columns"
            raise ValueError(error_message)

        # Ensure 'amount' column contains numeric values
        if not pd.api.types.is_numeric_dtype(spending_df["amount"]):
            error_message = "'amount' column must contain numeric values"
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
            f"Spending Breakdown (Source: {source.capitalize()})", wrap=True,
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
        error_message = f"Error reading the CSV file: {e}"
        logger.error(error_message)
        raise ValueError(error_message) from e


