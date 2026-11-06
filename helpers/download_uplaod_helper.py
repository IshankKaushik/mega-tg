import os
import math
import time
from pyrogram import Client
from pyrogram.types import Message

# Helper function for size formatting
def humanbytes(size):
    if not size:
        return "0 B"
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

# Helper function for ETA
def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
          ((str(hours) + "h, ") if hours else "") + \
          ((str(minutes) + "m, ") if minutes else "") + \
          ((str(seconds) + "s, ") if seconds else "")
    return tmp[:-2] if tmp else "0s"

# The live progress bar for uploads
async def progress_for_pyrogram(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    if round(diff % 5.00) == 0 or current == total:
        percentage = current * 100 / total
        speed = current / diff if diff > 0 else 0
        progress = "[{0}{1}] \n**Progress**: {2}%\n".format(
            ''.join(["●" for i in range(math.floor(percentage / 5))]),
            ''.join(["○" for i in range(20 - math.floor(percentage / 5))]),
            round(percentage, 2)
        )
        tmp = progress + "{0} of {1}\n**Speed**: {2}/s\n**ETA**: {3}\n".format(
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            TimeFormatter((total - current) / speed) if speed > 0 else "0s"
        )
        try:
            await message.edit_text(
                text=f"{ud_type}\n\n{tmp}",
                disable_web_page_preview=True
            )
        except Exception:
            pass

# Upload a single file
async def send_file(bot, update, tg_send_type, thumb_image_path, file_path, tmp_directory, description, usermsg):
    start_time = time.time()
    if tg_send_type == "vid":
        await bot.send_video(
            chat_id=update.chat.id,
            video=file_path,
            caption=description,
            thumb=thumb_image_path,
            progress=progress_for_pyrogram,
            progress_args=("🚀 **Uploading...**", usermsg, start_time)
        )
    else:
        await bot.send_document(
            chat_id=update.chat.id,
            document=file_path,
            caption=description,
            thumb=thumb_image_path,
            progress=progress_for_pyrogram,
            progress_args=("🚀 **Uploading...**", usermsg, start_time)
        )

# Upload split parts
async def send_splitted_file(bot, update, tg_send_type, thumb_image_path, file_path, tmp_directory, description, usermsg):
    await send_file(bot, update, tg_send_type, thumb_image_path, file_path, tmp_directory, description, usermsg)
