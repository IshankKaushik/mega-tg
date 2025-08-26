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

from translation import Translation
from database.blacklist import check_blacklist
from database.userchats import add_chat

@Client.on_message(filters.photo)
async def save_photo(bot, update: Message):
    """Save custom thumbnail"""
    try:
        user_id = update.from_user.id
        
        # Check blacklist
        if check_blacklist(user_id):
            await update.reply_text("❌ Sorry! You are banned from using this bot!")
            return
        
        # Add user to database
        add_chat(user_id)
        
        # Download and save thumbnail
        thumb_image_path = os.path.join(Config.DOWNLOAD_LOCATION, f"{user_id}.jpg")
        
        # Create download directory if it doesn't exist
        os.makedirs(Config.DOWNLOAD_LOCATION, exist_ok=True)
        
        # Download the photo
        await update.download(file_name=thumb_image_path)
        
        await update.reply_text(
            Translation.SAVED_CUSTOM_THUMB_NAIL,
            quote=True
        )
        
        logger.info(f"Custom thumbnail saved for user: {user_id}")
        
    except Exception as e:
        logger.error(f"Error saving thumbnail for user {update.from_user.id}: {e}")
        await update.reply_text(
            "❌ Error saving thumbnail. Please try again.",
            quote=True
        )

@Client.on_message(filters.command("deletethumbnail"))
async def delete_thumbnail(bot, update: Message):
    """Delete custom thumbnail"""
    try:
        user_id = update.from_user.id
        
        # Check blacklist
        if check_blacklist(user_id):
            await update.reply_text("❌ Sorry! You are banned from using this bot!")
            return
        
        # Add user to database
        add_chat(user_id)
        
        thumb_image_path = os.path.join(Config.DOWNLOAD_LOCATION, f"{user_id}.jpg")
        
        if os.path.exists(thumb_image_path):
            try:
                os.remove(thumb_image_path)
                await update.reply_text(
                    Translation.DEL_ETED_CUSTOM_THUMB_NAIL,
                    quote=True
                )
                logger.info(f"Custom thumbnail deleted for user: {user_id}")
            except Exception as e:
                logger.error(f"Error deleting thumbnail file: {e}")
                await update.reply_text(
                    "❌ Error deleting thumbnail file. Please try again.",
                    quote=True
                )
        else:
            await update.reply_text(
                "📝 No custom thumbnail found to delete!",
                quote=True
            )
            
    except Exception as e:
        logger.error(f"Error in delete thumbnail for user {update.from_user.id}: {e}")
        await update.reply_text(
            "❌ An error occurred while processing your request.",
            quote=True
        )

@Client.on_message(filters.command("mythumbnail"))
async def show_thumbnail(bot, update: Message):
    """Show current custom thumbnail"""
    try:
        user_id = update.from_user.id
        
        # Check blacklist
        if check_blacklist(user_id):
            await update.reply_text("❌ Sorry! You are banned from using this bot!")
            return
        
        # Add user to database
        add_chat(user_id)
        
        thumb_image_path = os.path.join(Config.DOWNLOAD_LOCATION, f"{user_id}.jpg")
        
        if os.path.exists(thumb_image_path):
            await update.reply_photo(
                photo=thumb_image_path,
                caption="🖼️ <b>Your Current Custom Thumbnail</b>\n\nThis will be used for your next uploads!",
                quote=True
            )
            logger.info(f"Thumbnail shown for user: {user_id}")
        else:
            await update.reply_text(
                "📝 <b>No Custom Thumbnail Set</b>\n\n"
                "Send me a photo to set it as your custom thumbnail for uploads!",
                quote=True
            )
            
    except Exception as e:
        logger.error(f"Error showing thumbnail for user {update.from_user.id}: {e}")
        await update.reply_text(
            "❌ An error occurred while processing your request.",
            quote=True
        )
