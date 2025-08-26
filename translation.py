import os

if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

class Translation(object):
    START_TEXT = f"""<b>Hello there,</b>
    
I am a <b>Mega Link Downloader</b> bot! 🚀

Just enter your mega.nz link and I will return the file/video to you!😇

💠 I can set custom captions and custom thumbnails too!

💠 I can download links which are bigger than 2GB too! 😍

💠 <b>NEW:</b> Now using file-based storage (no Redis needed)!

Press /help for more details!

✨ <b>I am open source so you can make your own bot from here!👇</b>

<b>🔧 Updated Version Features:</b>
• Improved error handling
• Better logging system
• File-based data storage
• Enhanced performance
• Modern Python practices"""
    
    DOWNLOAD_START = "<b>Downloading to my server now 📥</b> \n\n<code>Please wait, uploading will start as soon as possible😇...</code>"
    UPLOAD_START = "Uploading to Telegram now 📤..."
    AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS = "Downloaded in <b>{}</b> seconds.\n\nUploaded in <b>{}</b> seconds.\n\n<b>Thanks For Using This Free Service</b> ❤️"
    SAVED_CUSTOM_THUMB_NAIL = "𝗖𝘂𝘀𝘁𝗼𝗺 𝗧𝗵𝘂𝗺𝗯𝗻𝗮𝗶𝗹 𝗜𝘀 𝗦𝗮𝘃𝗲𝗱. 𝗧𝗵𝗶𝘀 𝗜𝗺𝗮𝗴𝗲 𝗪𝗶𝗹𝗹 𝗕𝗲 𝗨𝘀𝗲𝗱 𝗜𝗻 𝗬𝗼𝘂𝗿 𝗡𝗲𝘅𝘁 𝗨𝗽𝗹𝗼𝗮𝗱𝘀 📁.\n\nIf you want to delete it send\n /deletethumbnail anytime!"
    DEL_ETED_CUSTOM_THUMB_NAIL = "𝗖𝘂𝘀𝘁𝗼𝗺 𝗧𝗵𝘂𝗺𝗯𝗻𝗮𝗶𝗹 𝗖𝗹𝗲𝗮𝗿𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 ❌.\nYou will now get an auto generated thumbnail for your video uploads!"

    HELP_USER = f"""<b><u>🍁Hi I am a Mega Link Downloader Bot.. 🍁</u></b>
 
<u>How to use me:-</u>

<b>Just Send me a mega.nz file link!</b>

<b>Important:-</b> 

- Folder links are not supported.

- Your link should be valid(not expired or been removed) and should not be password protected or encrypted or private!

❇️ <b>If you want a custom thumbnail for your uploads send a photo before sending the mega link!.</b> <i>(This step is Optional)</i>

💠 It means it is not necessary to send an image to include as a thumbnail.
If you don't send a thumbnail the video/file will be uploaded with an auto generated thumbnail from the video.
The thumbnail you send will be used for your next uploads!

press /deletethumbnail if you want to delete the previously saved thumbnail.
(Then the video will be uploaded with an auto-generated thumbnail!)

❇️ <b>Special feature</b> :- <i>Set caption to any file you want!</i>

💠 Select an uploaded file/video or forward me <b>Any Telegram File</b> and Just write the text you want to be on the file as a reply to the File by selecting it (as replying to a message😅) and the text you wrote will be attached as caption!😍

Ex:- <a href="https://telegra.ph/file/bdc35efc07712050bc418.jpg">Send Like This! It's Easy🥳</a>

<b>Note</b> :- You can download links which are bigger than 2GB from me too! Due to telegram API limits I can't upload files which are bigger than 2GB so I will split such files and upload them to you!

<b>🆕 Updated Features:</b>
• File-based storage (no Redis dependency)
• Improved error handling and logging
• Better performance and stability
• Enhanced admin controls
• Automatic backups

✨ <b>I am open source so you can make your own bot from here!👇</b>"""

    # Error messages
    ERROR_INVALID_LINK = "❌ <b>Invalid Link!</b>\n\nMake sure your link is:\n• Valid (not expired or removed)\n• Not password protected\n• Not encrypted or private"
    ERROR_FOLDER_NOT_SUPPORTED = "❌ <b>Folder links are not supported!</b>\n\nPlease send individual file links only."
    ERROR_NOT_MEGA_LINK = "❌ <b>I am a mega.nz link downloader bot! 😑</b>\n\nThis is not a mega.nz link. 😡"
    ERROR_DOWNLOAD_FAILED = "❌ <b>Download Failed!</b>\n\nPlease try again later or check if the link is still valid."
    ERROR_UPLOAD_FAILED = "❌ <b>Upload Failed!</b>\n\nThe file might be too large or corrupted."
    ERROR_PROCESSING = "❌ <b>Processing Error!</b>\n\nAn error occurred while processing your request."
    
    # Success messages
    SUCCESS_DOWNLOAD_COMPLETE = "✅ <b>Download Complete!</b>\n\nStarting upload to Telegram..."
    SUCCESS_UPLOAD_COMPLETE = "✅ <b>Upload Complete!</b>\n\nThank you for using this service! ❤️"
    
    # Info messages
    INFO_PROCESSING = "⏳ <b>Processing...</b>\n\nPlease wait while I analyze your link..."
    INFO_SPLITTING_FILE = "✂️ <b>Splitting File...</b>\n\nThe file is larger than 2GB, splitting into smaller parts..."
    INFO_GENERATING_THUMBNAIL = "🖼️ <b>Generating Thumbnail...</b>\n\nCreating thumbnail for your video..."
