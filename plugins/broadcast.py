from pyrogram import Client, filters
import logging
import os

from database.userchats import get_all_chats, get_user_count

# Configure logging
logger = logging.getLogger(__name__)

# Import configuration
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

@Client.on_message(filters.command("broadcast") & filters.user(int(Config.OWNER_ID)))
async def broadcast_message(client, message):
    """Broadcast message to all users"""
    try:
        if message.reply_to_message:
            MSG = message.reply_to_message
        else:
            return await message.reply_text(
                "First send me the message that you want to send to the other users of this bot! "
                "<b>Then as a reply to it send <code>/broadcast</code></b>"
            )
        
        m = await message.reply_text("`Broadcasting...`")
        ALLCHATS = get_all_chats()
        
        if not ALLCHATS:
            await m.edit_text("No users found in database!")
            return
        
        SUCE = 0
        FAIL = 0
        STR = "ERROR Report !\n\n"
        
        for chat in ALLCHATS:
            try:
                await MSG.copy(chat)
                SUCE += 1
            except Exception as e:
                FAIL += 1
                STR += f"{chat} - {str(e)}\n"
                logger.warning(f"Failed to broadcast to {chat}: {e}")
        
        result_text = f"Successfully Broadcasted to {SUCE} Chats\nFailed - {FAIL} Chats!"
        await message.reply_text(result_text)
        
        if FAIL > 0:
            await m.edit_text("Generating Error Report!")
            try:
                with open("ErrorReport.txt", "w") as f:
                    f.write(STR)
                await message.reply_document("ErrorReport.txt", caption="Errors on Broadcast")
                os.remove("ErrorReport.txt")
            except Exception as e:
                logger.error(f"Error creating error report: {e}")
        
        await m.delete()
        logger.info(f"Broadcast completed: {SUCE} success, {FAIL} failed")
        
    except Exception as e:
        logger.error(f"Error in broadcast: {e}")
        await message.reply_text(f"Error occurred during broadcast: {str(e)}")

@Client.on_message(filters.command("stats") & filters.user(int(Config.OWNER_ID)))
async def get_stats(_, message):
    """Get bot statistics"""
    try:
        from database.blacklist import get_blacklist_count
        
        total_users = get_user_count()
        blacklisted_users = get_blacklist_count()
        active_users = total_users - blacklisted_users
        
        stats_text = f"""
<b>📊 Bot Statistics</b>

<b>👥 Total Users:</b> {total_users}
<b>✅ Active Users:</b> {active_users}
<b>🚫 Blacklisted Users:</b> {blacklisted_users}
<b>👑 Auth Users:</b> {len(Config.AUTH_USERS)}

<b>📁 Storage:</b> File-based (Redis-free)
<b>🤖 Bot:</b> {Config.Bot_username}
        """
        
        await message.reply_text(stats_text, quote=True)
        logger.info(f"Stats requested by owner: {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        await message.reply_text(f"Error getting statistics: {str(e)}")

@Client.on_message(filters.command("backup") & filters.user(int(Config.OWNER_ID)))
async def create_backup(_, message):
    """Create backup of bot data"""
    try:
        from database.file_db import DB
        
        m = await message.reply_text("Creating backup...")
        
        backup_path = DB.backup()
        await m.edit_text(f"Backup created successfully at: `{backup_path}`")
        
        # Send backup as archive
        import shutil
        archive_path = f"{backup_path}.zip"
        shutil.make_archive(backup_path, 'zip', backup_path)
        
        await message.reply_document(
            archive_path,
            caption=f"Bot data backup\nCreated: {backup_path}"
        )
        
        # Cleanup
        os.remove(archive_path)
        shutil.rmtree(backup_path)
        
        logger.info(f"Backup created by owner: {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        await message.reply_text(f"Error creating backup: {str(e)}")

@Client.on_message(filters.command("logs") & filters.user(int(Config.OWNER_ID)))
async def get_logs(_, message):
    """Get recent bot logs"""
    try:
        from datetime import datetime
        
        log_file = f"logs/bot_{datetime.now().strftime('%Y%m%d')}.log"
        
        if os.path.exists(log_file):
            # Get last 100 lines
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_logs = ''.join(lines[-100:])
            
            if len(recent_logs) > 4000:  # Telegram message limit
                # Send as file
                await message.reply_document(log_file, caption="Recent bot logs")
            else:
                await message.reply_text(f"<pre>{recent_logs}</pre>", parse_mode="html")
        else:
            await message.reply_text("No log file found for today.")
            
        logger.info(f"Logs requested by owner: {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        await message.reply_text(f"Error getting logs: {str(e)}")
