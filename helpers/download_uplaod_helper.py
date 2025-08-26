import logging
import asyncio
import math
import os
import time
from PIL import Image
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

# Configure logging
logger = logging.getLogger(__name__)

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from translation import Translation

async def send_splitted_file(bot, update, tg_send_type, thumb_image_path, splited_file, tmp_directory_for_each_user, description, usermsg):
    """Send splitted file to user"""
    try:
        width = 0
        height = 0
        duration = 0
        
        if tg_send_type != "doc":
            try:
                metadata = extractMetadata(createParser(splited_file))
                if metadata is not None and metadata.has("duration"):
                    duration = metadata.get('duration').seconds
            except Exception as e:
                logger.warning(f"Could not extract metadata: {e}")
        
        # Handle thumbnail
        if os.path.exists(thumb_image_path):
            try:
                width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata and metadata.has("width"):
                    width = metadata.get("width")
                if metadata and metadata.has("height"):
                    height = metadata.get("height")
                
                Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                
                if tg_send_type == "doc":
                    img = img.resize((320, height if height > 0 else 320))
                else:
                    img = img.resize((90, height if height > 0 else 90))
                img.save(thumb_image_path)
                
            except Exception as e:
                logger.warning(f"Error processing thumbnail: {e}")
        else:
            try:
                thumb_image_path = await take_screen_shot(
                    splited_file,
                    tmp_directory_for_each_user,
                    (duration / 2) if duration > 0 else 10
                )
            except Exception as e:
                logger.warning(f"Could not generate thumbnail: {e}")
                thumb_image_path = None
        
        start_time = time.time()
        
        if tg_send_type == "vid":
            await update.reply_chat_action("upload_video")
            await bot.send_video(
                chat_id=update.chat.id,
                video=splited_file,
                caption=description,
                parse_mode="HTML",
                duration=duration,
                width=300,
                height=200,
                supports_streaming=True,
                thumb=thumb_image_path,
                reply_to_message_id=update.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    usermsg,
                    start_time
                )
            )
        elif tg_send_type == "doc":
            await update.reply_chat_action("upload_document")
            await bot.send_document(
                chat_id=update.chat.id,
                document=splited_file,
                thumb=thumb_image_path,
                caption=description,
                parse_mode="HTML",
                reply_to_message_id=update.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    usermsg,
                    start_time
                )
            )
            
    except Exception as e:
        logger.error(f"Error sending splitted file: {e}")
        raise

async def send_file(bot, update, tg_send_type, thumb_image_path, download_directory, tmp_directory_for_each_user, description, usermsg):
    """Send file to user"""
    try:
        width = 0
        height = 0
        duration = 0
        
        if tg_send_type != "doc":
            try:
                metadata = extractMetadata(createParser(download_directory))
                if metadata is not None and metadata.has("duration"):
                    duration = metadata.get('duration').seconds
            except Exception as e:
                logger.warning(f"Could not extract metadata: {e}")
        
        # Handle thumbnail
        if os.path.exists(thumb_image_path):
            try:
                width = 0
                height = 0
                metadata = extractMetadata(createParser(thumb_image_path))
                if metadata and metadata.has("width"):
                    width = metadata.get("width")
                if metadata and metadata.has("height"):
                    height = metadata.get("height")
                
                Image.open(thumb_image_path).convert("RGB").save(thumb_image_path)
                img = Image.open(thumb_image_path)
                
                if tg_send_type == "doc":
                    img = img.resize((320, height if height > 0 else 320))
                else:
                    img = img.resize((90, height if height > 0 else 90))
                img.save(thumb_image_path)
                
            except Exception as e:
                logger.warning(f"Error processing thumbnail: {e}")
        else:
            try:
                thumb_image_path = await take_screen_shot(
                    download_directory,
                    tmp_directory_for_each_user,
                    (duration / 2) if duration > 0 else 10
                )
            except Exception as e:
                logger.warning(f"Could not generate thumbnail: {e}")
                thumb_image_path = None
        
        start_time = time.time()
        
        if tg_send_type == "vid":
            await update.reply_chat_action("upload_video")
            await bot.send_video(
                chat_id=update.chat.id,
                video=download_directory,
                caption=description,
                parse_mode="HTML",
                duration=duration,
                width=300,
                height=200,
                supports_streaming=True,
                thumb=thumb_image_path,
                reply_to_message_id=update.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    usermsg,
                    start_time
                )
            )
        elif tg_send_type == "doc":
            await update.reply_chat_action("upload_document")
            await bot.send_document(
                chat_id=update.chat.id,
                document=download_directory,
                thumb=thumb_image_path,
                caption=description,
                parse_mode="HTML",
                reply_to_message_id=update.message_id,
                progress=progress_for_pyrogram,
                progress_args=(
                    Translation.UPLOAD_START,
                    usermsg,
                    start_time
                )
            )
            
    except Exception as e:
        logger.error(f"Error sending file: {e}")
        raise

async def progress_for_pyrogram(current, total, ud_type, message, start):
    """Progress callback for pyrogram uploads"""
    try:
        now = time.time()
        diff = now - start
        
        if round(diff % 10.00) == 0 or current == total:
            percentage = current * 100 / total
            speed = current / diff if diff > 0 else 0
            elapsed_time = round(diff) * 1000
            time_to_completion = round((total - current) / speed) * 1000 if speed > 0 else 0
            estimated_total_time = elapsed_time + time_to_completion
            
            bot_name = Config.Bot_username
            elapsed_time = TimeFormatter(milliseconds=elapsed_time)
            estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

            progress = "[{0}{1}] \n\n○ <b>Percentage ⚡️ :</b> {2}%\n\n○ <b>Finished ✅ :</b> ".format(
                ''.join(["●" for i in range(math.floor(percentage / 5))]),
                ''.join(["○" for i in range(20 - math.floor(percentage / 5))]),
                round(percentage, 2))

            tmp = progress + "{0} of {1}\n\n○ <b>Speed 🚀 :</b> {2}/s\n\n○ <b>Time left 🌝 :</b> {3}\n\n<b>uploading by {4}</b>\n".format(
                humanbytes(current),
                humanbytes(total),
                humanbytes(speed),
                estimated_total_time if estimated_total_time != '' else "0 s",
                bot_name
            )
            
            try:
                await message.edit(
                    text="{}\n {}".format(ud_type, tmp)
                )
            except Exception as e:
                logger.warning(f"Could not update progress: {e}")
                
    except Exception as e:
        logger.error(f"Error in progress callback: {e}")

def humanbytes(size):
    """Convert bytes to human readable format"""
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    """Format milliseconds to human readable time"""
    try:
        seconds, milliseconds = divmod(int(milliseconds), 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        
        tmp = ((str(days) + "d, ") if days else "") + \
            ((str(hours) + "h, ") if hours else "") + \
            ((str(minutes) + "m, ") if minutes else "") + \
            ((str(seconds) + "s, ") if seconds else "") + \
            ((str(milliseconds) + "ms, ") if milliseconds else "")
        return tmp[:-2]
    except Exception as e:
        logger.error(f"Error formatting time: {e}")
        return "0s"
  
async def take_screen_shot(video_file, output_directory, ttl):
    """Generate screenshot from video file"""
    try:
        out_put_file_name = os.path.join(output_directory, f"{int(time.time())}.jpg")
        
        file_genertor_command = [
            "ffmpeg",
            "-ss",
            str(ttl),
            "-i",
            video_file,
            "-vframes",
            "1",
            out_put_file_name,
            "-y"  # Overwrite output file
        ]
        
        process = await asyncio.create_subprocess_exec(
            *file_genertor_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        
        stdout, stderr = await process.communicate()
        
        if os.path.exists(out_put_file_name):
            return out_put_file_name
        else:
            logger.warning(f"Screenshot generation failed: {stderr.decode()}")
            return None
            
    except Exception as e:
        logger.error(f"Error generating screenshot: {e}")
        return None
