"""Emergency Fund Calculator Tool."""
import sys
from pathlib import Path

from loguru import logger

# Add project root to sys.path for module imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_setup import setup_logging
from utils.models import EmergencyFundInput

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"

# Set up logging at module level (only needed if this is a standalone file)
logging_configs = setup_logging(str(DEFAULT_CONFIG_PATH))
logger.info("Logging initialized for emergency_fund_calculator")


def calculate_emergency_fund(input_data: EmergencyFundInput) -> dict:
    """Calculate the ideal emergency fund size and track progress.

    Args:
        input_data (EmergencyFundInput): Validated input data using Pydantic.

    Returns:
        dict: Emergency fund details including target size, progress, and storage tips.

    """
    logger.info("Calculating emergency fund with validated inputs.")

    # Extract validated inputs
    monthly_expenses = input_data.monthly_expenses
    financial_obligations = input_data.financial_obligations
    months_coverage = input_data.months_coverage
    current_savings = input_data.current_savings

    # Calculate total monthly cost
    total_monthly_cost = monthly_expenses + financial_obligations

    # Calculate ideal fund size
    target_fund_size = total_monthly_cost * months_coverage

    # Calculate progress
    if target_fund_size > 0:
        progress_percentage = (current_savings / target_fund_size) * 100
    else:
        progress_percentage = 0


    remaining_amount = max(0, target_fund_size - current_savings)

    # Storage suggestions
    storage_tips = [
        "High-yield savings account: Offers better interest rates with easy access.",
        "Money market account: Balances liquidity and returns.",
        "Short-term CDs: Higher interest for fixed terms, but less flexibility.",
        "Avoid stocks or volatile investments for emergency funds due to risk.",
    ]

    result = {
        "monthly_expenses": monthly_expenses,
        "financial_obligations": financial_obligations,
        "months_coverage": months_coverage,
        "target_fund_size": target_fund_size,
        "current_savings": current_savings,
        "progress_percentage": round(progress_percentage, 2),
        "remaining_amount": remaining_amount,
        "storage_tips": storage_tips,
    }

    logger.info(f"""Emergency fund calculated: target={target_fund_size},
                progress={progress_percentage:.2f}%""")
    return result
