"""FastAPI Application for Financial Dashboard Assistant."""

import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from loguru import logger
from pydantic import BaseModel

sys.path.append(str(Path(__file__).parent.parent))
from llm.query_llm import query_financial_agent  # Import from existing agent
from utils.logging_setup import setup_logging

# Constants
PROJECT_ROOT = Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"

# Set up logging
logging_configs = setup_logging(str(DEFAULT_CONFIG_PATH))
logger.info("Logging initialized for financial_api.py")

# Initialize FastAPI app
app = FastAPI(
    title="Financial Dashboard API",
    description="API for querying a financial assistant with specialized tools.",
    version="1.0.0",
)


# Define request model
class QueryRequest(BaseModel):
    """Model for incoming query requests."""

    prompt: str


# Define response model
class QueryResponse(BaseModel):
    """Model for API responses."""

    response: str
    status: str
    details: dict[str, Any] | None = None


def raise_http_exception(status_code: int, detail: str) -> None:
    """Raise an HTTPException with the given status code and detail."""
    logger.error(f"Raising HTTPException: {detail}")
    raise HTTPException(status_code=status_code, detail=detail)

@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint to verify API is running."""
    logger.info("Health check requested")
    return {"status": "healthy", "message": "Financial Dashboard API is running"}


@app.post("/query")
async def query_assistant(request: QueryRequest) -> QueryResponse:
    """Query the financial assistant with a user prompt.

    Args:
    ----
        request: The incoming request containing the prompt.

    Returns:
    -------
        QueryResponse: The assistant's response and status.

    Raises:
    ------
        HTTPException: If the query fails or an error occurs.

    """
    prompt = request.prompt.strip()
    if not prompt:
        logger.error("Empty prompt received")
        raise_http_exception(400, "Prompt cannot be empty")

    logger.info(f"Received query: {prompt}")
    try:
        response = query_financial_agent(prompt)
        if "Error processing query" in response:
            logger.error(f"Query failed: {response}")
            raise_http_exception(status_code=500, detail=response)

        logger.info(f"Query successful: {response}")
        return QueryResponse(
            response=response,
            status="success",
            details=None,  # Could extend to include tool outputs if desired
        )
    except Exception as e:
        error_message = f"Failed to process query: {e!s}"
        logger.error(error_message)
        raise HTTPException(status_code=500, detail=error_message) from e


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI app with Uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
