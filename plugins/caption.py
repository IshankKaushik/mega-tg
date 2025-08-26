import logging
import os
from pyrogram import Client, filters
from pyrogram.types import Message

# Configure logging
logger = logging.getLogger(__name__)

# Import configuration
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from database.blacklist import check_blacklist
from database.userchats import add_chat

@Client.on_message(filters.reply & filters.text)
async def add_custom_caption(bot, update: Message):
    """Add custom caption to files"""
    try:
        user_id = update.from_user.id
        
        # Check blacklist
        if check_blacklist(user_id):
            await update.reply_text("❌ Sorry! You are banned from using this bot!")
            return
        
        # Add user to database
        add_chat(user_id)
        
        # Check if replying to a document or video
        replied_message = update.reply_to_message
        
        if not replied_message:
            return
        
        # Check if the replied message has a document or video
        if not (replied_message.document or replied_message.video or replied_message.audio or replied_message.photo):
            return
        
        # Get the custom caption
        custom_caption = update.text
        
        if len(custom_caption) > 1024:
            await update.reply_text(
                "❌ <b>Caption too long!</b>\n\n"
                "Telegram allows maximum 1024 characters in caption. "
                f"Your caption has {len(custom_caption)} characters.",
                quote=True
            )
            return
        
        # Copy the file with new caption
        try:
            if replied_message.document:
                await replied_message.copy(
                    chat_id=update.chat.id,
                    caption=custom_caption,
                    parse_mode="HTML"
                )
            elif replied_message.video:
                await replied_message.copy(
                    chat_id=update.chat.id,
                    caption=custom_caption,
                    parse_mode="HTML"
                )
            elif replied_message.audio:
                await replied_message.copy(
                    chat_id=update.chat.id,
                    caption=custom_caption,
                    parse_mode="HTML"
                )
            elif replied_message.photo:
                await replied_message.copy(
                    chat_id=update.chat.id,
                    caption=custom_caption,
                    parse_mode="HTML"
                )
            
            await update.reply_text(
                "✅ <b>Custom caption added successfully!</b>\n\n"
                "Your file has been re-uploaded with the new caption.",
                quote=True
            )
            
            logger.info(f"Custom caption added by user: {user_id}")
            
        except Exception as e:
            logger.error(f"Error copying file with caption: {e}")
            await update.reply_text(
                "❌ <b>Error adding caption!</b>\n\n"
                "Could not copy the file with new caption. Please try again.",
                quote=True
            )
            
    except Exception as e:
        logger.error(f"Error in caption handler for user {update.from_user.id}: {e}")
        await update.reply_text(
            "❌ An error occurred while processing your request.",
            quote=True
        )

@Client.on_message(filters.command("captionhelp"))
async def caption_help(bot, update: Message):
    """Show help for caption feature"""
    try:
        user_id = update.from_user.id
        
        # Check blacklist
        if check_blacklist(user_id):
            await update.reply_text("❌ Sorry! You are banned from using this bot!")
            return
        
        # Add user to database
        add_chat(user_id)
        
        help_text = """
<b>📝 How to Add Custom Captions</b>

<b>Step 1:</b> Forward any file (document, video, audio, photo) to this bot or upload a file.

<b>Step 2:</b> Reply to that file with the text you want as caption.

<b>Step 3:</b> The bot will re-upload the file with your custom caption!

<b>📋 Example:</b>
1. Send a video file to the bot
2. Reply to that video with: "My awesome video 🎬"
3. Bot will send the same video with your custom caption

<b>⚠️ Note:</b>
• Maximum caption length: 1024 characters
• HTML formatting is supported
• Works with all file types

<b>🎨 HTML Formatting Examples:</b>
• <code>&lt;b&gt;Bold text&lt;/b&gt;</code>
• <code>&lt;i&gt;Italic text&lt;/i&gt;</code>
• <code>&lt;u&gt;Underlined text&lt;/u&gt;</code>
• <code>&lt;code&gt;Monospace text&lt;/code&gt;</code>
        """
        
        await update.reply_text(help_text, quote=True)
        logger.info(f"Caption help shown to user: {user_id}")
        
    except Exception as e:
        logger.error(f"Error showing caption help: {e}")
        await update.reply_text(
            "❌ An error occurred while processing your request.",
            quote=True
        )
