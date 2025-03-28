"""Configuration loader."""

import tomllib
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).parent / "configs.toml"

def load_config() -> dict[str, Any]:
    """Load the configuration from the TOML file."""
    try:
        with CONFIG_PATH.open("rb") as f:
            return tomllib.load(f)
    except OSError as e:  # Catch specific exceptions instead of a blind `Exception`
        error_message = f"Failed to load config from {CONFIG_PATH}: {e}"
        raise ValueError(error_message) from e  # Use `raise ... from e` for clarity
