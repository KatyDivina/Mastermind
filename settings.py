import logging
import sys

file_handler = logging.FileHandler(filename="tmp.log")
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    handlers=handlers,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y.%m.%d %H:%M:%S",
)

CORRECT = "🟢"
WRONG_PLACE = "🟡"
INCORRECT = "🔴"

LOCK = "🔒"
UNLOCK = "🔓"
STAR = "⭐"

emoji = [
    "1️⃣",
    "2️⃣",
    "3️⃣",
    "4️⃣",
    "5️⃣",
    "6️⃣",
    "7️⃣",
    "8️⃣",
    "9️⃣",
    "🔟",
]
