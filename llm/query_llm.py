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
from tools.investment_tools import calculate_investment_return
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
        name="calculate_investment_return",
        func=lambda **kwargs: calculate_investment_return(
            InvestmentReturnInput(**kwargs),
        ),
        description=(
            "Calculate return. Expects {'symbol': str, 'initial_amount': float, "
            "'start_date': 'YYYY-MM-DD', 'end_date': 'YYYY-MM-DD'}."
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
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
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

if __name__ == "__main__":
    queries = [
        # Crypto queries
        "How much did Solana price increase from 2023-01-01 to 2023-12-31?",
        "What’s the price growth of Solana between January 1, 2023, and December 31, 2023?",
        "Can you tell me how much Solana went up from the start to the end of 2023?",
        "If I had Solana on Jan 1, 2023, how much more is it worth by Dec 31, 2023?",

        # Emergency fund queries
        # "If my monthly expenses are $3,000, how large should my emergency fund be?",
        # "What’s the suggested emergency savings amount for someone spending $2,500 monthly?",
        # "Based on $4,000 monthly expenses, what’s the recommended emergency fund size?",
        # "How much do I need to save for emergencies if I spend $5,000 per month?",
        # "What’s the target emergency fund amount for $3,500 in monthly expenses?",

        # Stock queries
        # "Fetch the historical stock prices for Apple from January 1, 2023, to December 31, 2023.",
        # "What were the price trends for Tesla between May 1, 2023, and August 31, 2023?",
        # "Retrieve the stock price history of Amazon shares for the entire year of 2023.",
        # "Can you pull up the stock data for Microsoft from the start of 2023 to the end of 2023?",
        # "Show me how Google's stock prices changed throughout 2023.",

        # Investment queries
        # "Calculate the return on my 10,000 investment if it grew to 12,000 in 2 years.",
        # "What’s the ROI if I invested 5,000 and it became 7,500 after 3 years?",
        # "How much profit would I make if I invested $20,000 and it doubled in 5 years?",
        # "What’s the annualized return on an investment that went from 1,000to1,500 in 1 year?",
        # "Compute the growth rate for an initial value of 15,000 and a finalvalueof 20,000 over 4 years.",

        # Spending queries
        # "What’s my spending breakdown for 2023?",
        # "How did I allocate my money in 2023?",
        # "Can you show me a detailed report of my expenses for 2023?",
        # "Break down my spending categories for the year 2023.",
        # "How much did I spend on different categories last year?",
        # "Provide an analysis of my spending habits in 2023.",
        ]
    for q in queries:
        response = query_financial_agent(q)
        print(f"Query: {q}\nResponse: {response}\n")
