"""Simulated data generator for testing."""

import secrets
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
from loguru import logger

# Add project root to sys.path for module imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_setup import setup_logging

# Define project root relative to this file (api/)
PROJECT_ROOT = Path(__file__).parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "spending_data.csv"

DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"

# Set up logging at module level
logging_configs = setup_logging(str(DEFAULT_CONFIG_PATH))
logger.info("Logging initialized for data_simulator.py")


def generate_spending_data(
        days: int = 365,
        user_profile: str = "average") -> pd.DataFrame:
    """Generate mock spending data based on a user profile.

    Args:
        days: Number of days to simulate (default: 365).
        user_profile: Spending profile ("average", "high_spender", "frugal").

    Returns:
        pd.DataFrame: Simulated spending data with 'category' and 'amount'.

    """
    logger.info(
        f"Generating mock spending data for {days} days, profile: {user_profile}",
    )

    # Define category ranges based on profile
    profiles = {
        "average": {
            "Food": (10, 100),
            "Housing": (500, 1500),
            "Entertainment": (20, 200),
            "Transportation": (5, 50),
            "Utilities": (50, 200),
            "Shopping": (10, 300),
        },
        "high_spender": {
            "Food": (50, 300),
            "Housing": (1000, 3000),
            "Entertainment": (100, 500),
            "Transportation": (20, 200),
            "Utilities": (100, 400),
            "Shopping": (50, 1000),
        },
        "frugal": {
            "Food": (5, 50),
            "Housing": (300, 800),
            "Entertainment": (5, 50),
            "Transportation": (2, 20),
            "Utilities": (20, 100),
            "Shopping": (5, 100),
        },
    }
    categories = profiles.get(user_profile, profiles["average"])

    # Use timezone-aware datetime
    start_date = datetime.now(UTC) - timedelta(days=days)
    dates = [start_date + timedelta(days=i) for i in range(days)]

    data = []
    for _date in dates:
        num_transactions = secrets.SystemRandom().randint(1, 5)
        for _ in range(num_transactions):
            category = secrets.SystemRandom().choice(list(categories.keys()))
            amount = secrets.SystemRandom().uniform(*categories[category])
            data.append({"category": category, "amount": round(amount, 2)})

    spending_data = pd.DataFrame(data)
    spending_agg = (
        spending_data.groupby("category")["amount"].sum().reset_index()
    )
    spending_data.to_csv(DATA_PATH, index=False)  # Save detailed data
    logger.info(f"Generated and saved mock spending data to {DATA_PATH}")
    return spending_agg



