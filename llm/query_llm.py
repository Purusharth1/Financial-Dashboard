"""Financial Dashboard Agent with LangChain."""

import sys
from pathlib import Path
from typing import NoReturn

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import StructuredTool
from langchain_ollama import ChatOllama
from loguru import logger

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))
from tools.crypto_tools import get_crypto_data
from tools.emergency_fund_tools import calculate_emergency_fund
from tools.investment_tools import calculate_investment_return_simple
from tools.spending_tools import get_spending_breakdown
from tools.stock_tools import get_stock_prices
from utils.configs import load_config
from utils.logging_setup import setup_logging
from utils.models import (
    CryptoInput,
    EmergencyFundInput,
    InvestmentReturnInput,
    SpendingBreakdownInput,
    StockPriceInput,
)

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"

# Set up logging
logging_configs = setup_logging(str(DEFAULT_CONFIG_PATH))
logger.info("Logging initialized for query_llm.py")

# Load LLM configuration
config = load_config()
MODEL_NAME = config["llm"]["default_model"]
SYSTEM_PROMPT = config["llm"]["system_prompt"]

# Define tools with StructuredTool
TOOLS: list[StructuredTool] = [
    StructuredTool.from_function(
        name="calculate_emergency_fund",
        func=lambda **kwargs: calculate_emergency_fund(EmergencyFundInput(**kwargs)),
        description="Calculate emergency fund. Expects {'monthly_expenses': float}.",
        args_schema=EmergencyFundInput,
    ),
    StructuredTool.from_function(
        name="get_stock_prices",
        func=lambda **kwargs: get_stock_prices(StockPriceInput(**kwargs)),
        description=(
            "Fetch stock prices. Expects {'symbol': str, 'start_date': 'YYYY-MM-DD', "
            "'end_date': 'YYYY-MM-DD'}."
        ),
        args_schema=StockPriceInput,
    ),
    StructuredTool.from_function(
        name="calculate_investment_return_simple",
        func=lambda **kwargs: calculate_investment_return_simple(
            InvestmentReturnInput(**kwargs),
        ),
        description=(
            """Calculate investment returns based on initial amount,
            time period, and annual return rate."""
            "Expects {'initial_amount': float, 'years': float, 'annual_return': float}."
        ),
        args_schema=InvestmentReturnInput,
    ),
    StructuredTool.from_function(
        name="get_crypto_data",
        func=lambda **kwargs: get_crypto_data(CryptoInput(**kwargs)),
        description=(
            "Fetch crypto prices. Expects {'crypto_id': str,'start_date': 'YYYY-MM-DD',"
            " 'end_date': 'YYYY-MM-DD', 'vs_currency': 'usd'}."
        ),
        args_schema=CryptoInput,
    ),
    StructuredTool.from_function(
        name="get_spending_breakdown",
        func=lambda **kwargs: get_spending_breakdown(SpendingBreakdownInput(**kwargs)),
        description="Retrieve spending data for a year. Expects {'year': str}.",
        args_schema=SpendingBreakdownInput,
    ),
]


def initialize_llm() -> AgentExecutor:
    """Initialize the LangChain agent."""
    llm = ChatOllama(model=MODEL_NAME, temperature=0)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ],
    )
    agent = create_tool_calling_agent(llm, TOOLS, prompt)
    executor = AgentExecutor(agent=agent, tools=TOOLS, verbose=True, max_iterations=4)
    logger.info("Financial agent initialized")
    return executor


agent_executor = initialize_llm()


def handle_invalid_response() -> NoReturn:
    """Raise an error for unexpected response formats."""
    error_message = "Unexpected response format"
    raise ValueError(error_message)


def query_financial_agent(prompt: str) -> str:
    """Query the financial agent."""
    logger.info(f"Processing query: {prompt}")
    max_retries = 4
    for attempt in range(max_retries):
        try:
            response = agent_executor.invoke({"input": prompt})
            if "output" not in response:
                handle_invalid_response()
            else:
                result = response["output"]
                logger.info(f"Agent response: {result}")
                return result
        except (KeyError, ValueError) as e:
            error_message = f"Attempt {attempt + 1}/{max_retries} failed: {e}"
            logger.error(error_message)
            if attempt == max_retries - 1:
                return f"Failed to process query after {max_retries} attempts: {e}"
    return "Unexpected error in retry loop"