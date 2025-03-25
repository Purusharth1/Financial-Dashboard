"""Module for querying the LLM.

This module provides a function to send prompts to an LLM and retrieve responses.
It includes error handling for common issues like connection errors or
invalid responses.
"""

import sys
import tomllib
from pathlib import Path

import ollama
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))
from utils.logging_setup import setup_logging  # Adjusted import path

# Define project root relative to this file (llm/)
PROJECT_ROOT = Path(__file__).parent.parent  # financial_dashboard/
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"

# Set up logging at module level
logging_configs = setup_logging(str(DEFAULT_CONFIG_PATH))
logger.info("Logging initialized for query_llm.py")


def load_config(config_file: str = str(DEFAULT_CONFIG_PATH)) -> dict:
    """Load configuration settings from a TOML file.

    Args:
        config_file (str): Path to the TOML configuration file.

    Returns:
        dict: Configuration settings.

    Raises:
        FileNotFoundError: If the configuration file is not found.
        ValueError: If the TOML format is invalid.

    """
    try:
        config_path = Path(config_file)  # No need to resolve relative to __file__
        with config_path.open("rb") as f:
            logger.debug(f"Loading config from {config_path}")
            return tomllib.load(f)
    except FileNotFoundError as fnf_err:
        error_message = f"Configuration file not found: {config_path}"
        logger.error(error_message)
        raise FileNotFoundError(error_message) from fnf_err
    except tomllib.TOMLDecodeError as decode_err:
        error_message = f"Invalid TOML format in file: {config_path}"
        logger.error(error_message)
        raise ValueError(error_message) from decode_err


def query_llm(prompt: str, model: str | None = None) -> str:
    """Send a query to the LLM and return the response.

    Args:
        prompt (str): The user's query or prompt.
        model (str | None): The LLM model to use. Defaults to the value in the config.

    Returns:
        str: The LLM's response or an error message if something goes wrong.

    Raises:
        RuntimeError: If there is an issue generating the response.

    """
    # Load configuration
    config = load_config()
    model = model or config["llm"]["default_model"]

    logger.info(f"Sending query to LLM: {prompt} (model: {model})")
    try:
        response = ollama.generate(model=model, prompt=prompt)
    except ollama.ResponseError as e:
        error_message = f"LLM Response Error: {e!s}"
        logger.error(error_message)
        return error_message
    except ConnectionError as conn_err:
        error_message = f"""Connection Error: Unable to
                            connect to Ollama server. Details: {conn_err!s}"""
        logger.error(error_message)
        return error_message
    except Exception as unexpected_err:
        logger.exception(f"Unexpected Error: {unexpected_err!s}")
        raise
    else:
        response_text = response["response"].strip() #Strip whitespace forcleaner output
        logger.info(f"Received response: {response_text}")
        return response_text


# Example usage
if __name__ == "__main__":
    prompt = "Who is the Chief Minister of Rajasthan?"
    response = query_llm(prompt)
    logger.info(f"Main execution response: {response}")
