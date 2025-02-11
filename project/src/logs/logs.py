import os
import logging
import logging.config

global logger
logger = logging

def initialize(logLevel:str) -> logging.Logger:
    """Initialize the logger

    Args:
        logLevel (str): The log level.

    Returns:
        logger: the logger
    """

    logger.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')