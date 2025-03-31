"""Financial Dashboard Agent with LangChain."""

import sys
from pathlib import Path

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from loguru import logger

# Add project root to sys.path for module imports
sys.path.append(str(Path(__file__).parent.parent))
from tools.crypto_tools import get_crypto_data
from tools.emergency_fund_tools import calculate_emergency_fund
from tools.investment_tools import calculate_investment_return
from tools.spending_tools import get_spending_breakdown
from tools.stock_tools import get_stock_prices
from utils.configs import load_config
from utils.logging_setup import setup_logging

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"

# Set up logging
logging_configs = setup_logging(str(DEFAULT_CONFIG_PATH))
logger.info("Logging initialized for financial_agent.py")

# Load LLM configuration
config = load_config()
MODEL_NAME = config["llm"]["default_model"]

# Define tools
TOOLS = [
    get_spending_breakdown,
    get_stock_prices,
    calculate_investment_return,
    get_crypto_data,
    calculate_emergency_fund,
]

# System prompt
SYSTEM_PROMPT = """
You are a financial assistant with access to specialized tools to analyze financial data and provide insights.
Use the tools available to answer user queries accurately. If a query doesn't require a tool, respond directly.
Provide concise, helpful answers based on the data or calculations from the tools.
"""


def create_financial_agent() -> AgentExecutor:
    """Create a LangChain agent with tool-calling capabilities."""
    # Initialize LLM
    llm = ChatOllama(model=MODEL_NAME, temperature=0)

    # Define prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            ("human", "{input}"),
            ("assistant", "{agent_scratchpad}"),
        ],
    )

    # Create agent
    agent = create_tool_calling_agent(llm, TOOLS, prompt)
    executor = AgentExecutor(agent=agent, tools=TOOLS, verbose=True)

    logger.info("Financial agent initialized")
    return executor


def query_financial_agent(prompt: str) -> str:
    """Query the financial agent and return the response."""
    executor = create_financial_agent()
    try:
        logger.info(f"Processing query: {prompt}")
        response = executor.invoke({"input": prompt})
        result = response["output"]
        logger.info(f"Agent response: {result}")
        return result
    except Exception as e:
        error_message = f"Error processing query: {e}"
        logger.error(error_message)
        return error_message


if __name__ == "__main__":
    # Example queries
    queries = [
        # "What is the current price of Tesla stock from 2023-01-01 to 2023-12-31?",
        # "How much emergency fund do I need if my monthly expenses are $2000?",
        # "Analyze my portfolio: {'AAPL': 0.5, 'TSLA': 0.5}",
        # "What’s my spending breakdown for 2023?",
        # "Analyze my spending breakdown for 2023 and show me where I spend the most?",
        "How much Solana price increase from 2023-01-01 to 2023-12-31?",
    ]
    for q in queries:
        response = query_financial_agent(q)
        print(f"Query: {q}\nResponse: {response}\n")
