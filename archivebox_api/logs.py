import logging
from rich.logging import RichHandler
import os
from .config import config

## Use similar log format as gunicorn:
# FORMAT = f"[%(asctime)s] [{os.getpid()}] [%(levelname)s] %(module)s - %(funcName)s: %(message)s"

## Use simple log format for use with RichHandler:
FORMAT = f"%(message)s"


def setup_logs():
    logging.basicConfig(
        level=getattr(logging, config["LOG_LEVEL"]),
        format=FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S %z",
        handlers=[RichHandler()],
    )
