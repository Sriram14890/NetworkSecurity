import logging as _stdlib_logging
from datetime import datetime
import os

# ---- log file setup ----
LOG_FILE = f"{datetime.now().strftime('%m_%d_%y_%H_%M_%S')}.log"

LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE)

# ---- configure stdlib logging ----
_stdlib_logging.basicConfig(
    filename=LOG_FILE_PATH,
    format="[%(asctime)s] %(lineno)d %(name)s - %(levelname)s - %(message)s",
    level=_stdlib_logging.INFO,
)

# ---- CRITICAL PART ----
# expose stdlib logging exactly as expected
logging = _stdlib_logging
getLogger = _stdlib_logging.getLogger
basicConfig = _stdlib_logging.basicConfig
INFO = _stdlib_logging.INFO
ERROR = _stdlib_logging.ERROR
WARNING = _stdlib_logging.WARNING
