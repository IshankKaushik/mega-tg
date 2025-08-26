import logging
import os

# Configure logging
logger = logging.getLogger(__name__)

# Import configuration
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from translation import Translation

import pyrogram
logging.getLogger("pyrogram").setLevel(logging.WARNING)

from database.blacklist import check_blacklist
from database.userchats import add_chat

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

REPLY_MARKUP = InlineKeyboardMarkup(
    [
        [InlineKeyboardButton("🚀 Deploy Yours Now! 😍", url="https://github.com/XMYSTERlOUSX/mega-link-downloader-bot")],
        [InlineKeyboardButton("📖 Updated Version", url="https://github.com/yourusername/mega-tg-updated")],
    ]
)

@Client.on_message(filters.command("help"))
async def help_user(bot, update):
    """Handle /help command"""
    try:
        fuser = update.from_user.id
        if check_blacklist(fuser):
            await update.reply_text("Sorry! You are Banned!")
            return
        
        add_chat(fuser)
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.HELP_USER,
            parse_mode="html",
            reply_markup=REPLY_MARKUP,
            disable_web_page_preview=True,
            reply_to_message_id=update.message_id
        )
        logger.info(f"Help command used by user: {fuser}")
        
    except Exception as e:
        logger.error(f"Error in help command: {e}")
        await update.reply_text("An error occurred while processing your request.")

@Client.on_message(filters.command("start"))
async def start(bot, update):
    """Handle /start command"""
    try:
        fuser = update.from_user.id
        if check_blacklist(fuser):
            await update.reply_text("Sorry! You are Banned!")
            return
        
        add_chat(fuser)
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.START_TEXT,
            reply_markup=REPLY_MARKUP,
            disable_web_page_preview=True,
            reply_to_message_id=update.message_id
        )
        logger.info(f"Start command used by user: {fuser}")
        
    except Exception as e:
        logger.error(f"Error in start command: {e}")
        await update.reply_text("An error occurred while processing your request.")

@Client.on_message(filters.command("about"))
async def about(bot, update):
    """Handle /about command"""
    try:
        fuser = update.from_user.id
        if check_blacklist(fuser):
            await update.reply_text("Sorry! You are Banned!")
            return
        
        add_chat(fuser)
        about_text = """
<b>🤖 Mega Link Downloader Bot - Updated Version</b>

<b>✨ Features:</b>
• Download mega.nz links without account
• Support for files up to 5GB
• Automatic file splitting for large files
• Custom thumbnail support
• Custom caption support
• Admin controls and user management
• File-based storage (no external database needed)
• Improved error handling and logging

<b>🔧 Technology:</b>
• Python 3.8+
• Pyrogram
• File-based data storage
• MEGAcmd & megatools

<b>📊 Version:</b> 2.0 (Updated)
<b>🗃️ Storage:</b> Text files (Redis-free)
        """
        
        await bot.send_message(
            chat_id=update.chat.id,
            text=about_text,
            parse_mode="html",
            reply_markup=REPLY_MARKUP,
            disable_web_page_preview=True,
            reply_to_message_id=update.message_id
        )
        logger.info(f"About command used by user: {fuser}")
        
    except Exception as e:
        logger.error(f"Error in about command: {e}")
        await update.reply_text("An error occurred while processing your request.")
