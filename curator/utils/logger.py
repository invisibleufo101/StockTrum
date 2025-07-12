import os
from dotenv import load_dotenv
import logging
from logging.handlers import TimedRotatingFileHandler

load_dotenv()
LOG_DIR = os.getenv("LOG_DIR")
os.makedirs(LOG_DIR, exist_ok = True)

fmt    = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
datef  = "%Y-%m-%d %H:%M:%S"
formatter = logging.Formatter(fmt=fmt, datefmt=datef)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

file_path = os.path.join(LOG_DIR, "app.log")
file_handler = TimedRotatingFileHandler(
    filename=file_path,
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8",
    utc=False,
)

file_handler.suffix = "%Y-%m-%d.log"
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(min(console_handler.level, file_handler.level))
for h in list(root_logger.handlers):
    root_logger.removeHandler(h)

root_logger.addHandler(console_handler)
root_logger.addHandler(file_handler)