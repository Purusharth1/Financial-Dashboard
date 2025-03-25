"""Module for setting up LLM models using Ollama."""

import sys
import tomllib
from pathlib import Path

import ollama
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))

from utils.logging_setup import setup_logging

# Define project root relative to this file (llm/)
PROJECT_ROOT = Path(__file__).parent.parent  # financial_dashboard/
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"

# Set up logging at module level
logging_configs = setup_logging(str(DEFAULT_CONFIG_PATH))
logger.info("Logging initialized for llama_setup.py")

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
        config_path = Path(__file__).parent / config_file  # Resolve relative path
        with config_path.open("rb") as f:  # Use Path.open() instead of open()
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


def setup_llm() -> None:
    """Set up the LLM by downloading the model (if not already downloaded)."""
    # Load configuration
    config = load_config()
    model_name = config["llm"]["model_name"]

    try:
        logger.info("Checking if the model is already downloaded...")
        ollama.show(model_name)
        logger.info("Model is already downloaded.")
    except ollama.ResponseError as e:
        if "not found" in str(e):
            logger.info("Model not found. Downloading the model...")
            try:
                ollama.pull(model_name)
                logger.info("Model download complete.")
            except Exception as pull_error:
                error_message = f"Failed to download the model: {pull_error}"
                logger.error(error_message)
                raise RuntimeError(error_message) from pull_error
        else:
            error_message = f"Error checking model status: {e}"
            logger.error(error_message)
            raise RuntimeError(error_message) from e
    except ConnectionError as conn_error:
        error_message = (
            f"Failed to connect to Ollama server: {conn_error}. "
            "Please ensure the Ollama server is running and accessible."
        )
        logger.error(error_message)
        raise ConnectionError(error_message) from conn_error


if __name__ == "__main__":
    setup_llm()
