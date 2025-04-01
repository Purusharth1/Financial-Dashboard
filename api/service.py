"""Financial Dashboard Assistant Service Module."""

import sys
from pathlib import Path
from typing import Any

from loguru import logger

import bentoml

# Update sys.path using pathlib
sys.path.append(str(Path(__file__).resolve().parent.parent))

from llm.query_llm import query_financial_agent  # Import from existing agent
from utils.logging_setup import setup_logging   # Import from existing setup

# Set up unified logging
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"
setup_logging(str(DEFAULT_CONFIG_PATH))
logger.info("Logging initialized for financial_assistant service")

@bentoml.service
class FinancialAssistant:
    """Class for managing the financial assistant service."""

    def __init__(self) -> None:
        """Initialize the financial assistant service."""
        logger.info("Financial Assistant service initialized")

    @bentoml.api
    def health_check(self) -> dict[str, str]:
        """Health check endpoint to verify API is running."""
        logger.info("Health check requested")
        return {"status": "healthy", "message": "Financial Dashboard API is running"}

    @bentoml.api
    def query_assistant(self, prompt: str) -> dict[str, Any]:
        """Query the financial assistant with a user prompt.

        Args:
            prompt: The user's query string.

        Returns:
            A dictionary with the response, status, and optional details.
        """
        prompt = prompt.strip()
        if not prompt:
            logger.error("Empty prompt received")
            return {"status": "error", "response": "Prompt cannot be empty"}

        logger.info(f"Received query: {prompt}")
        try:
            response = query_financial_agent(prompt)
            if "Error processing query" in response:
                logger.error(f"Query failed: {response}")
                return {"status": "error", "response": response}
            
            logger.info(f"Query successful: {response}")
            return {"response": response, "status": "success", "details": None}
        except Exception as e:
            error_message = f"Failed to process query: {str(e)}"
            logger.error(error_message)
            return {"status": "error", "response": error_message}

if __name__ == "__main__":
    # Example usage
    assistant = FinancialAssistant()
    health_result = assistant.health_check()
    logger.info(f"Health check result: {health_result}")
    query_result = assistant.query_assistant("What is the current stock price?")
    logger.info(f"Query result: {query_result}")