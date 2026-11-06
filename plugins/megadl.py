import logging
import asyncio
import subprocess
import os
import shutil
import time
from datetime import datetime
from asyncio import get_running_loop
import concurrent.futures

# Configure logging
logger = logging.getLogger(__name__)

# Import helpers
from helpers.download_uplaod_helper import send_splitted_file, send_file, humanbytes
from helpers.files_spliiting import split_files, split_video_files

# Import configuration
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from translation import Translation

import pyrogram
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup

# Set pyrogram logging level
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# Import database functions
from database.blacklist import check_blacklist
from database.userchats import add_chat

# Global variables for download management
active_downloads = {}
download_semaphore = asyncio.Semaphore(Config.MAX_CONCURRENT_DOWNLOADS)

class MegaDownloader:
    """Reliable Mega downloader using only megatools"""
    
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
    
    async def get_mega_info(self, url):
        """Get mega file information using megatools with retry logic"""
        loop = get_running_loop()
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                # 使用 megatools 获取文件信息，增加超时时间和调试输出
                result = await loop.run_in_executor(
                    self.executor,
                    self._get_info_with_megatools,
                    url
                )
                if result.get('success'):
                    return result
                logger.warning(f"Megatools attempt {attempt + 1} failed: {result.get('error')}")
            except Exception as e:
                logger.error(f"Error in get_mega_info attempt {attempt + 1}: {e}")
            
            # 每次重试前等待 2 秒
            await asyncio.sleep(2)
            
        return {'success': False, 'error': 'Failed after multiple retries'}
    
    def _get_info_with_megatools(self, url):
        """Get file info using megatools command (blocking)"""
        try:
            # 关键修改：增加 --debug 参数，并将超时时间设为 180 秒
            result = subprocess.run(
                ["megadl", "--print-names", "--no-progress", "--debug", url],
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')
                if lines:
                    filename = lines[-1].strip()
                    if filename:
                        return {
                            'name': filename,
                            'size': 0,
                            'success': True
                        }
            
            # 如果失败，将 stderr 记录到日志中以便排查
            logger.error(f"Megatools stderr: {result.stderr}")
            return {'success': False, 'error': 'Could not get file information from megatools'}
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Timeout (180s) while getting file info'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    async def download_with_megatools(self, url, download_path, cred_location=None):
        """Download using megatools"""
        try:
            loop = get_running_loop()
            await loop.run_in_executor(
                self.executor,
                self._download_megatools,
                url,
                download_path,
                cred_location
            )
            return True
        except Exception as e:
            logger.error(f"Megatools download failed: {e}")
            raise
    
    def _download_megatools(self, url, download_path, cred_location=None):
        """Download using megatools (blocking)"""
        try:
            cmd = ["megadl", url, "--path", download_path]
            
            if cred_location and os.path.exists(cred_location):
                cmd.extend(["--config", cred_location])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=Config.DOWNLOAD_TIMEOUT
            )
            
            if result.returncode != 0:
                raise Exception(f"Megatools failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            raise Exception("Download timeout")
        except Exception as e:
            raise Exception(f"Megatools error: {str(e)}")

# Global downloader instance
mega_downloader = MegaDownloader()

@Client.on_message(filters.regex(pattern=".*http.*"))
async def mega_dl(bot, update):
    """Main mega download handler"""
    user_id = update.from_user.id
    try:
        if check_blacklist(user_id):
            await update.reply_text("❌ Sorry! You are banned from using this bot!")
            return
        add_chat(user_id)
        url = update.text.strip()
        if "mega.nz" not in url.lower():
            await update.reply_text(Translation.ERROR_NOT_MEGA_LINK)
            return
        if any(x in url for x in ["folder", "#F", "#N"]):
            await update.reply_text(Translation.ERROR_FOLDER_NOT_SUPPORTED)
            return
        if user_id in active_downloads:
            await update.reply_text("⚠️ You already have an active download! Please wait for it to complete.")
            return
        
        async with download_semaphore:
            active_downloads[user_id] = True
            try:
                await process_mega_download(bot, update, url, user_id)
            finally:
                active_downloads.pop(user_id, None)
                
    except Exception as e:
        logger.error(f"Error in mega_dl for user {user_id}: {e}")
        await update.reply_text(f"❌ An unexpected error occurred: {str(e)}")
        active_downloads.pop(user_id, None)

async def process_mega_download(bot, update, url, user_id):
    """Process mega download"""
    usermsg = None
    tmp_directory = None
    try:
        usermsg = await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.INFO_PROCESSING,
            reply_to_message_id=update.id
        )
        
        file_info = await mega_downloader.get_mega_info(url)
        if not file_info.get('success'):
            await usermsg.edit_text(f"{Translation.ERROR_INVALID_LINK}\n\nError: {file_info.get('error', 'Unknown error')}")
            return
        
        filename = file_info.get('name', 'unknown_file')
        filesize = file_info.get('size', 0)
        tg_send_type = "vid" if any(ext in filename.lower() for ext in ['.mp4', '.mkv', '.avi', '.mov']) else "doc"
        description = os.path.splitext(filename)[0] if '.' in filename else filename
        is_auth_user = user_id == int(Config.OWNER_ID) or user_id in Config.AUTH_USERS
        
        if is_auth_user:
            admin_dir_name = str(int(time.time()))
            tmp_directory = os.path.join(Config.ADMIN_LOCATION, str(user_id), admin_dir_name)
        else:
            tmp_directory = os.path.join(Config.DOWNLOAD_LOCATION, str(user_id))
        
        os.makedirs(tmp_directory, exist_ok=True)
        download_path = os.path.join(tmp_directory, filename)
        thumb_image_path = os.path.join(Config.DOWNLOAD_LOCATION, f"{user_id}.jpg")
        cred_location = os.path.join(Config.CREDENTIALS_LOCATION, "mega.ini")
        
        await usermsg.edit_text(f"<b>📁 File detected:</b> {filename}\n<b>📊 Size:</b> {humanbytes(filesize) if filesize > 0 else 'Unknown'}\n\n{Translation.DOWNLOAD_START}")
        
        start_time = datetime.now()
        
        # 只使用 megatools 进行下载
        await mega_downloader.download_with_megatools(url, tmp_directory, cred_location)
        
        if not os.path.exists(download_path):
            await usermsg.edit_text(Translation.ERROR_DOWNLOAD_FAILED)
            return
        
        actual_size = os.path.getsize(download_path)
        end_download = datetime.now()
        download_time = (end_download - start_time).seconds
        
        if actual_size > Config.MAX_FILE_SIZE:
            await handle_large_file(bot, update, usermsg, download_path, tmp_directory, filename, tg_send_type, thumb_image_path, description, actual_size, download_time)
        else:
            await handle_normal_file(bot, update, usermsg, download_path, tmp_directory, tg_send_type, thumb_image_path, description, download_time)
            
    except Exception as e:
        logger.error(f"Error processing download for user {user_id}: {e}")
        if usermsg:
            await usermsg.edit_text(f"{Translation.ERROR_PROCESSING}\n\nError: {str(e)}")
    finally:
        if tmp_directory and os.path.exists(tmp_directory):
            try:
                shutil.rmtree(tmp_directory)
            except Exception as e:
                logger.warning(f"Could not cleanup directory {tmp_directory}: {e}")

# ... (handle_large_file 和 handle_normal_file 函数保持不变)
async def handle_large_file(bot, update, usermsg, download_path, tmp_directory, filename, tg_send_type, thumb_image_path, description, file_size, download_time):
    """Handle files larger than 2GB"""
    try:
        await usermsg.edit_text(f"<b>📊 Detected Size:</b> {humanbytes(file_size)}\n\n{Translation.INFO_SPLITTING_FILE}")
        split_directory = os.path.join(tmp_directory, "split")
        os.makedirs(split_directory, exist_ok=True)
        
        if tg_send_type == "vid":
            await split_video_files(download_path, Config.SPLIT_SIZE, split_directory, filename)
        else:
            loop = get_running_loop()
            await loop.run_in_executor(None, split_files, download_path, Config.SPLIT_SIZE, split_directory)
        
        split_files_list = []
        for root, dirs, files in os.walk(split_directory):
            for file in files:
                if file != "fs_manifest.csv":
                    split_files_list.append(os.path.join(root, file))
        
        split_files_list.sort()
        upload_start = datetime.now()
        
        for i, split_file in enumerate(split_files_list, 1):
            split_filename = os.path.basename(split_file)
            split_description = f"{description} - Part {i}/{len(split_files_list)}"
            await usermsg.edit_text(f"{Translation.UPLOAD_START}\n\nUploading part {i}/{len(split_files_list)}: {split_filename}")
            await send_splitted_file(bot, update, tg_send_type, thumb_image_path, split_file, tmp_directory, split_description, usermsg)
        
        upload_end = datetime.now()
        upload_time = (upload_end - upload_start).seconds
        await usermsg.edit_text(Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(download_time, upload_time))
    except Exception as e:
        logger.error(f"Error handling large file: {e}")
        await usermsg.edit_text(f"{Translation.ERROR_UPLOAD_FAILED}\n\nError: {str(e)}")

async def handle_normal_file(bot, update, usermsg, download_path, tmp_directory, tg_send_type, thumb_image_path, description, download_time):
    """Handle normal sized files"""
    try:
        await usermsg.edit_text(Translation.UPLOAD_START)
        upload_start = datetime.now()
        await send_file(bot, update, tg_send_type, thumb_image_path, download_path, tmp_directory, description, usermsg)
        upload_end = datetime.now()
        upload_time = (upload_end - upload_start).seconds
        await usermsg.edit_text(Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(download_time, upload_time))
    except Exception as e:
        logger.error(f"Error handling normal file: {e}")
        await usermsg.edit_text(f"{Translation.ERROR_UPLOAD_FAILED}\n\nError: {str(e)}")
