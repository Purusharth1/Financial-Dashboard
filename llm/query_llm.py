"""Module for querying the LLM.

This module provides a function to send prompts to an LLM and retrieve responses.
It includes error handling for common issues like connection
    errors or invalid responses.
"""

import tomllib
from pathlib import Path

import ollama


def load_config(config_file: str = "../utils/configs.toml") -> dict:
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
            return tomllib.load(f)
    except FileNotFoundError as fnf_err:
        error_message = f"Configuration file not found: {config_path}"
        raise FileNotFoundError(error_message) from fnf_err
    except tomllib.TOMLDecodeError as decode_err:
        error_message = f"Invalid TOML format in file: {config_path}"
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

    try:
        # Send the prompt to the LLM
        response = ollama.generate(model=model, prompt=prompt)
        return response["response"].strip()  # Strip whitespace for cleaner output
    except ollama.ResponseError as e:
        return f"LLM Response Error: {e!s}"
    except ConnectionError as conn_err:
        return f"""Connection Error: Unable to
                    connect to Ollama server. Details: {conn_err!s}"""
    except Exception as unexpected_err:
        # Log the unexpected error before re-raising it
        print(f"Unexpected Error: {unexpected_err!s}")
        raise  # Re-raise the exception to avoid silencing critical issues


# Example usage
if __name__ == "__main__":
    prompt = "Who is the Chief Minister of Rajasthan?"
    response = query_llm(prompt)
    print(response)
