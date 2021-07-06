from dotenv import load_dotenv
from corded.logging import get_logger

load_dotenv()

from src.bot import bot

logger = get_logger()
logger.info("Bot starting...")
bot.start()
