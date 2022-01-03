import logging

logging.basicConfig(
    filename="logs.txt",
    level=logging.INFO,
    format="\n%(asctime)s | %(levelname)s | %(message)s",
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
