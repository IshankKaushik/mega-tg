import logging
import asyncio
import subprocess
import os
import shutil
import time
from datetime import datetime
from asyncio import get_running_loop
import concurrent.futures
import requests

# Configure logging
logger = logging.getLogger(__name__)

# Import helpers
from helpers.download_uplaod_helper import send_splitted_file, send_file, humanbytes, progress_for_pyrogram, TimeFormatter
from helpers.files_spliiting import split_files, split_video_files

# Import configuration
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

from translation import Translation

import pyrogram
from pyrogram import Client, filters

logging.getLogger("pyrogram").setLevel(logging.WARNING)

from database.blacklist import check_blacklist
from database.userchats import add_chat

active_downloads = {}
download_semaphore = asyncio.Semaphore(Config.MAX_CONCURRENT_DOWNLOADS)

class MegaDownloader:
    def __init__(self):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=3)
    
    async def get_mega_info(self, url):
        loop = get_running_loop()
        try:
            result = await loop.run_in_executor(self.executor, self._get_info_sync, url)
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_info_sync(self, url):
        try:
            from mega import Mega
            m = Mega().login() # Logs in anonymously if no credentials provided
            file_info = m.get_public_url_info(url)
            if file_info and 'size' in file_info and 'name' in file_info:
                return {
                    'size': int(file_info['size']),
                    'name': file_info['name'],
                    'success': True
                }
        except Exception as e:
            logger.error(f"mega.py info error: {e}")
        return {'success': False, 'error': 'mega.py failed'}

    async def download_with_progress(self, url, download_dir, message, start_time):
        """Streams the download and updates Telegram message"""
        loop = get_running_loop()
        try:
            from mega import Mega
            # If Mega credentials are set in env, use them to bypass limits
            m = Mega().login(Config.Mega_email, Config.Mega_password) if Config.Mega_email else Mega().login()
            file_info = m.get_public_url_info(url)
            download_url = m.get_download_url(file_info)
            
            file_path = os.path.join(download_dir, file_info['name'])
            
            # Use requests to stream and update progress
            with requests.get(download_url, stream=True, timeout=300) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded = 0
                last_update_time = time.time()
                
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024): # 1MB chunks
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Update every 5 seconds
                            if time.time() - last_update_time > 5:
                                percentage = (downloaded / total_size) * 100 if total_size > 0 else 0
                                speed = downloaded / (time.time() - start_time)
                                eta = (total_size - downloaded) / speed if speed > 0 else 0
                                
                                progress_str = f"📥 **Downloading...**\n\n"
                                progress_str += f"**Progress:** {percentage:.1f}%\n"
                                progress_str += f"**Size:** {humanbytes(downloaded)} / {humanbytes(total_size)}\n"
                                progress_str += f"**Speed:** {humanbytes(speed)}/s\n"
                                progress_str += f"**ETA:** {TimeFormatter(eta)}"
                                
                                try:
                                    await message.edit_text(progress_str)
                                except Exception:
                                    pass
                                last_update_time = time.time()
            return file_path
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise

mega_downloader = MegaDownloader()

@Client.on_message(filters.regex(pattern=".*http.*"))
async def mega_dl(bot, update):
    user_id = update.from_user.id
    try:
        if check_blacklist(user_id):
            await update.reply_text("❌ Sorry! You are banned.")
            return
        add_chat(user_id)
        url = update.text.strip()
        
        if "mega.nz" not in url.lower():
            await update.reply_text("❌ Invalid link. Please send a Mega.nz link.")
            return
            
        if user_id in active_downloads:
            await update.reply_text("⚠️ You already have an active download!")
            return
        
        async with download_semaphore:
            active_downloads[user_id] = True
            try:
                await process_mega_download(bot, update, url, user_id)
            finally:
                active_downloads.pop(user_id, None)
                
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.reply_text(f"❌ Error: {str(e)}")

async def process_mega_download(bot, update, url, user_id):
    usermsg = None
    tmp_directory = None
    try:
        usermsg = await bot.send_message(chat_id=update.chat.id, text="🔍 Fetching file info...", reply_to_message_id=update.id)
        
        file_info = await mega_downloader.get_mega_info(url)
        if not file_info.get('success'):
            await usermsg.edit_text(f"❌ Failed to get file info. Error: {file_info.get('error')}")
            return
        
        filename = file_info.get('name', 'unknown_file')
        filesize = file_info.get('size', 0)
        
        # Create temp directory
        tmp_directory = os.path.join(Config.DOWNLOAD_LOCATION, str(user_id))
        os.makedirs(tmp_directory, exist_ok=True)
        
        await usermsg.edit_text(f"📁 **File:** {filename}\n📊 **Size:** {humanbytes(filesize)}\n\n⏳ Starting download...")
        
        start_time = time.time()
        
        # Download with live progress
        download_path = await mega_downloader.download_with_progress(url, tmp_directory, usermsg, start_time)
        
        if not os.path.exists(download_path):
            await usermsg.edit_text("❌ Download failed. File not found.")
            return
        
        actual_size = os.path.getsize(download_path)
        
        # Check if file needs splitting
        if actual_size > Config.MAX_FILE_SIZE:
            await handle_large_file(bot, update, usermsg, download_path, tmp_directory, filename, actual_size)
        else:
            await handle_normal_file(bot, update, usermsg, download_path, tmp_directory, filename)
            
    except Exception as e:
        logger.error(f"Error processing: {e}")
        if usermsg:
            await usermsg.edit_text(f"❌ Error: {str(e)}")
    finally:
        if tmp_directory and os.path.exists(tmp_directory):
            try:
                shutil.rmtree(tmp_directory)
            except Exception:
                pass

async def handle_large_file(bot, update, usermsg, download_path, tmp_directory, filename, file_size):
    try:
        await usermsg.edit_text(f"✂️ **File is larger than 2GB.**\nSplitting into parts...")
        split_directory = os.path.join(tmp_directory, "split")
        os.makedirs(split_directory, exist_ok=True)
        
        # Split the file (keep extension)
        # Using split_files from your repo, ensure it splits correctly
        loop = get_running_loop()
        await loop.run_in_executor(None, split_files, download_path, Config.SPLIT_SIZE, split_directory)
        
        # Get list of split files
        split_files_list = sorted([os.path.join(split_directory, f) for f in os.listdir(split_directory)])
        
        for i, split_file in enumerate(split_files_list, 1):
            part_name = f"{filename}.part{i}"
            # Rename to keep extension (e.g., video.mp4.part1)
            new_path = os.path.join(split_directory, part_name)
            os.rename(split_file, new_path)
            
            await usermsg.edit_text(f"🚀 Uploading part {i}/{len(split_files_list)}...")
            
            # Upload with progress
            await send_splitted_file(bot, update, "doc", None, new_path, tmp_directory, part_name, usermsg)
            
        await usermsg.edit_text("🎉 All parts uploaded successfully!")
    except Exception as e:
        logger.error(f"Large file error: {e}")
        await usermsg.edit_text(f"❌ Upload failed: {str(e)}")

async def handle_normal_file(bot, update, usermsg, download_path, tmp_directory, filename):
    try:
        await usermsg.edit_text("🚀 Uploading to Telegram...")
        await send_file(bot, update, "doc", None, download_path, tmp_directory, filename, usermsg)
        await usermsg.edit_text("🎉 File uploaded successfully!")
    except Exception as e:
        logger.error(f"Normal file error: {e}")
        await usermsg.edit_text(f"❌ Upload failed: {str(e)}")
