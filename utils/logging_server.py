"""Logging server module.

This module implements a logging server that receives log messages over the network
and logs them to a file.
"""
import sys
from pathlib import Path

import zmq

sys.path.append(str(Path(__file__).parent.parent))
from loguru import logger

from utils.config_types import LoggingConfigs
from utils.logging_setup import setup_logging

# Define project root
PROJECT_ROOT = Path(__file__).parent.parent  # financial_dashboard/
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "utils" / "configs.toml"

def set_logging_configs(logging_configs: LoggingConfigs) -> None:
    """Configure the logger with the provided logging settings.

    Args:
        logging_configs (LoggingConfigs): The logging configuration to apply.

    """
    logger.remove()
    logger.add(
        logging_configs.log_file_name,
        rotation=logging_configs.log_rotation,
        compression=logging_configs.log_compression,
        format=logging_configs.server_log_format,
        level=logging_configs.min_log_level,
        enqueue=True,
        backtrace=True,
        diagnose=True,
    )


def start_logging_server(logging_configs: LoggingConfigs) -> None:
    """Start the logging server to receive and process log messages.

    Args:
        logging_configs (LoggingConfigs): The logging configuration including
        server port.

    """
    socket = zmq.Context().socket(zmq.SUB)
    socket.bind(f"tcp://127.0.0.1:{logging_configs.log_server_port}")
    socket.subscribe("")
    while True:
        try:
            ret_val = socket.recv_multipart()
            log_level_name, message = ret_val
            log_level_name = log_level_name.decode("utf8").strip()
            message = message.decode("utf8").strip()
            logger.log(log_level_name, message)
        except zmq.ZMQError as e:
            logger.exception(f"ZMQ error when logging: {e}")


if __name__ == "__main__":
    logging_configs = setup_logging(str(DEFAULT_CONFIG_PATH))
    set_logging_configs(logging_configs)
    start_logging_server(logging_configs)
