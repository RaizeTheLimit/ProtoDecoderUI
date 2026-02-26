#!/usr/bin/env python3
"""
Logger utility - exact replica of JavaScript logging
"""

import logging
import os
from pathlib import Path

def setup_logging(log_level="INFO"):
    """Setup logging - exact replica of JavaScript logging setup"""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Convert string log level to logging constant
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR
    }
    
    level = level_map.get(log_level.upper(), logging.INFO)
    
    # Setup logging configuration
    logging.basicConfig(
        level=level,
        format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler(logs_dir / "app.log"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("ProtoDecoder")
