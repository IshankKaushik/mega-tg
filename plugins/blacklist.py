from pyrogram import Client, filters
import logging
import os

from database.blacklist import add_blacklist, get_blacklisted, remove_blacklist, get_blacklist_count

# Configure logging
logger = logging.getLogger(__name__)

# Import configuration
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

@Client.on_message(filters.command("black") & filters.user(int(Config.OWNER_ID)))
async def blacklist_user(_, message):
    """Add user to blacklist"""
    try:
        try:
            user_id = int(message.text.split(" ", maxsplit=1)[1])
        except (IndexError, ValueError):
            return await message.reply_text(
                "<b>Send this command in the below format👇</b>\n\n"
                "<code>/black userid</code> (Replace 'userid' with the user's telegram id of who you want to ban from the bot!)"
            )
        
        success = add_blacklist(user_id)
        if success:
            await message.reply_text(f"✅ Blacklisted user: <code>{user_id}</code>")
            logger.info(f"User {user_id} blacklisted by owner")
        else:
            await message.reply_text(f"⚠️ User <code>{user_id}</code> is already blacklisted!")
            
    except Exception as e:
        logger.error(f"Error blacklisting user: {e}")
        await message.reply_text(f"Error blacklisting user: {str(e)}")

@Client.on_message(filters.command("unblack") & filters.user(int(Config.OWNER_ID)))
async def unblacklist_user(_, message):
    """Remove user from blacklist"""
    try:
        try:
            user_id = int(message.text.split(" ", maxsplit=1)[1])
        except (IndexError, ValueError):
            return await message.reply_text(
                "<b>Send this command in the below format👇</b>\n\n"
                "<code>/unblack userid</code> (Replace 'userid' with the user's telegram id of who you want to unban from the bot!)"
            )
        
        result = remove_blacklist(user_id)
        await message.reply_text(f"✅ {result}")
        
        if "Removed" in result:
            logger.info(f"User {user_id} removed from blacklist by owner")
            
    except Exception as e:
        logger.error(f"Error removing user from blacklist: {e}")
        await message.reply_text(f"Error removing user from blacklist: {str(e)}")

@Client.on_message(filters.command("listblack") & filters.user(int(Config.OWNER_ID)))
async def list_blacklisted(_, message):
    """List all blacklisted users"""
    try:
        m = await message.reply_text("Getting blacklisted users...")
        
        blacklisted_users = get_blacklisted()
        blacklist_count = get_blacklist_count()
        
        if not blacklisted_users:
            await m.edit_text("📝 Blacklist is empty!")
            return
        
        # Create formatted list
        blacklist_text = f"<b>🚫 Blacklisted Users ({blacklist_count})</b>\n\n"
        
        for i, user_id in enumerate(blacklisted_users, 1):
            blacklist_text += f"{i}. <code>{user_id}</code>\n"
            
            # Split into multiple messages if too long
            if len(blacklist_text) > 3500:
                await m.edit_text(blacklist_text)
                m = await message.reply_text("Continuing...")
                blacklist_text = ""
        
        if blacklist_text:
            await m.edit_text(blacklist_text)
        
        logger.info(f"Blacklist requested by owner: {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error listing blacklisted users: {e}")
        await message.reply_text(f"Error getting blacklisted users: {str(e)}")

@Client.on_message(filters.command("clearblacklist") & filters.user(int(Config.OWNER_ID)))
async def clear_blacklist(_, message):
    """Clear all blacklisted users (with confirmation)"""
    try:
        from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        blacklist_count = get_blacklist_count()
        
        if blacklist_count == 0:
            await message.reply_text("📝 Blacklist is already empty!")
            return
        
        # Create confirmation keyboard
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes, Clear All", callback_data="confirm_clear_blacklist"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_clear_blacklist")
            ]
        ])
        
        await message.reply_text(
            f"⚠️ <b>Warning!</b>\n\n"
            f"This will remove all <b>{blacklist_count}</b> users from the blacklist.\n"
            f"This action cannot be undone!\n\n"
            f"Are you sure you want to continue?",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error in clear blacklist: {e}")
        await message.reply_text(f"Error: {str(e)}")

@Client.on_callback_query(filters.regex("confirm_clear_blacklist"))
async def confirm_clear_blacklist(_, callback_query):
    """Confirm and clear blacklist"""
    try:
        # Check if user is owner
        if callback_query.from_user.id != int(Config.OWNER_ID):
            await callback_query.answer("❌ Unauthorized!", show_alert=True)
            return
        
        from database.file_db import DB
        
        # Clear blacklist
        DB.set("blacklist", {"USERS": []})
        
        await callback_query.edit_message_text(
            "✅ <b>Blacklist cleared successfully!</b>\n\n"
            "All users have been removed from the blacklist."
        )
        
        logger.info(f"Blacklist cleared by owner: {callback_query.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error clearing blacklist: {e}")
        await callback_query.edit_message_text(f"Error clearing blacklist: {str(e)}")

@Client.on_callback_query(filters.regex("cancel_clear_blacklist"))
async def cancel_clear_blacklist(_, callback_query):
    """Cancel blacklist clearing"""
    try:
        # Check if user is owner
        if callback_query.from_user.id != int(Config.OWNER_ID):
            await callback_query.answer("❌ Unauthorized!", show_alert=True)
            return
        
        await callback_query.edit_message_text("❌ Blacklist clearing cancelled.")
        
    except Exception as e:
        logger.error(f"Error cancelling blacklist clear: {e}")
        await callback_query.answer("Error occurred!", show_alert=True)
