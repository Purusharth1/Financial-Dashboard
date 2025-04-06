"""Locust load testing for Financial Dashboard API."""
import secrets
from typing import Any

from locust import HttpUser, between, task

HTTP_STATUS_OK = 200  # Constant for HTTP status code 200

class FinancialUser(HttpUser):
    """Simulate a user interacting with the Financial Dashboard API."""

    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks

    # FastAPI host (default) - override with --host on command line for BentoML
    host: str = "http://127.0.0.1:8000"

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize user with prompts for each task type."""
        super().__init__(*args, **kwargs)
        # Define prompts once during initialization to avoid recreating them each task
        self.spending_prompts = [
            "What's my spending breakdown for 2023?",
            "How did I spend my money in 2023?",
            "Show me where my money went in 2023?",
        ]
        self.crypto_prompts = [
            "How much did Solana price increase from 2023-01-01 to 2023-12-31?",
            (
                "What's the price growth of Solana between January 1, 2023, "
                "and December 31, 2023?"
            ),
            (
                "Can you tell me how much Solana went up from the start to "
                "the end of 2023?"
            ),
        ]
        self.emergency_prompt = (
            "What's my emergency fund need if my spending in 2023 was $24,000 total?"
        )
        self.investment_prompt = (
            "If Solana grew by 50% and my stocks by 20%, what's my total return "
            "on $1000 split evenly?"
        )

    def _make_query(self, prompt: str, name: str) -> dict[str, Any]:
        """Make a query to the API with proper error handling.

        Args:
            prompt: The query prompt to send
            name: Name of the request for Locust statistics
        Returns:
            The response from the API

        """
        # Works with both FastAPI and BentoML endpoints
        with self.client.post(
            "/query",
            json={"prompt": prompt},
            name=name,
            catch_response=True,
            timeout=500,
        ) as response:
            if response.status_code != HTTP_STATUS_OK:
                response.failure(f"Failed with status code: {response.status_code}")
            else:
                try:
                    data = response.json()
                    if data.get("status") == "error":
                        response.failure(f"API returned error: {data.get('response')}")
                except ValueError:
                    response.failure("Invalid JSON response")
            return response

    @task(1)
    def health_check(self) -> None:
        """Test the health check endpoint."""
        # Works with both FastAPI and BentoML
        with self.client.get(
            "/health", name="Health Check", catch_response=True,
        ) as response:
            if response.status_code != HTTP_STATUS_OK:
                response.failure(f"Health check failed: {response.status_code}")

    @task(4)
    def query_spending_breakdown(self) -> None:
        """Test spending breakdown queries."""
        # Use random.choice instead of self.random to avoid Ruff linting errors
        prompt = secrets.choice(self.spending_prompts)
        self._make_query(prompt, "Spending Breakdown")

    @task(2)
    def query_crypto_data(self) -> None:
        """Test crypto price queries."""
        prompt = secrets.choice(self.crypto_prompts)
        self._make_query(prompt, "Crypto Data")

    @task(1)
    def query_emergency_fund(self) -> None:
        """Test emergency fund calculation."""
        self._make_query(self.emergency_prompt, "Emergency Fund")

    @task(1)
    def query_investment_return(self) -> None:
        """Test investment return calculation."""
        self._make_query(self.investment_prompt, "Investment Return")
