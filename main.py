from dotenv import load_dotenv
from loguru import logger

load_dotenv()

from src.bot import bot

logger.info("Bot starting...")
bot.start()
