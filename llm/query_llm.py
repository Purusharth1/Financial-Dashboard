"""Financial Dashboard Agent with LangChain."""

import sys
from pathlib import Path

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import Tool
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

# Define tools with detailed descriptions for better LLM understanding
TOOLS: list[Tool] = [
    Tool(
        name="get_spending_breakdown",
        func=get_spending_breakdown,
        description=(
            "Retrieve and analyze spending data for a given year or data source. "
            "Returns a breakdown of spending categories and total spent."
        ),
    ),
    Tool(
        name="get_stock_prices",
        func=get_stock_prices,
        description=(
            "Fetch historical stock prices for a given symbol between start "
            "and end dates."
        ),
    ),
    Tool(
        name="calculate_investment_return",
        func=calculate_investment_return,
        description=(
            "Calculate the return on an investment given initial value, final value, "
            "and time period."
        ),
    ),
    Tool(
        name="get_crypto_data",
        func=get_crypto_data,
        description=(
            "Fetch historical cryptocurrency prices for a given symbol between start "
            "and end dates."
        ),
    ),
    Tool(
        name="calculate_emergency_fund",
        func=calculate_emergency_fund,
        description=(
            "Calculate the recommended emergency fund size based on monthly expenses."
        ),
    ),
]

# Enhanced system prompt
SYSTEM_PROMPT = (
    "You are a financial assistant designed to interpret a wide range of user queries "
    "and provide accurate, concise answers using specialized tools. Your goals are:\n\n"
    "1. **Understand Paraphrasing**: Recognize different ways a user might ask the same"
    ' question (e.g., "What\'s my spending breakdown?" vs "How did I spend my money?") '
    "and map them to the appropriate tool or direct response.\n"
    "2. **Compose Tools Systematically**: When a query requires multiple steps (e.g., "
    "fetching data and calculating returns), use tools in the correct order and respect"
    " logical precedence (e.g., multiplication before addition in calculations).\n"
    "3. **Provide Clear Answers**: Return results in a user-friendly format, avoiding "
    "unnecessary complexity.\n\n"
    "Available tools:\n"
    "- get_spending_breakdown: For spending analysis.\n"
    "- get_stock_prices: For stock price data.\n"
    "- calculate_investment_return: For investment growth calculations.\n"
    "- get_crypto_data: For cryptocurrency price data.\n"
    "- calculate_emergency_fund: For emergency fund recommendations.\n\n"
    "If a query doesn't require a tool, respond directly with your knowledge. If "
    "multiple tools are needed, chain them logically. For example, to answer 'How much "
    "did Solana grow from 2023-01-01 to 2023-12-31?', first fetch the price data "
    "with get_crypto_data, then calculate the return with calculate_investment_return."
)

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
    logger.info(f"Processing query: {prompt}")

    try:
        response = executor.invoke({"input": prompt})
        if "output" in response:
            result = response["output"]
            logger.info(f"Agent response: {result}")
        else:
            error_message = "Unexpected response format from the agent."
            logger.error(error_message)
            return error_message
    except (ValueError, RuntimeError, AttributeError, KeyError) as e:
        error_message = f"Error processing query: {e}"
        logger.error(error_message)
        return error_message
    except Exception as e:  # Fallback for unexpected errors
        logger.critical(f"Critical unexpected error: {e}")
        raise  # Re-raise to avoid silent failure
    else:
        return result

if __name__ == "__main__":
    # Test queries with paraphrasing and tool intersection
    queries = [
        # Paraphrasing for crypto price increase
        "How much did Solana price increase from 2023-01-01 to 2023-12-31?",
        "What's the price growth of Solana between January 1, 2023,"
        "and December 31, 2023?",
        "Can you tell me how much Solana went up from the start to the end of 2023?",
        "If I had Solana on Jan 1, 2023, how much more is it worth by Dec 31, 2023?",
    ]
    for q in queries:
        response = query_financial_agent(q)
        logger.info(f"Query: {q}\nResponse: {response}\n")
        print(f"Query: {q}\nResponse: {response}\n")
