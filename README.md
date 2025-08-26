# Mega Link Downloader Bot - Updated Version

<p align="center"><b>A modernized Telegram bot to download mega.nz links without Redis dependency!</b></p>

<p align="center">
<img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
<img src="https://img.shields.io/badge/Pyrogram-2.0+-green.svg" alt="Pyrogram">
<img src="https://img.shields.io/badge/Storage-File%20Based-orange.svg" alt="Storage">
</p>

## 🚀 What's New in This Version

- ✅ **Redis-Free**: No external database dependencies - uses simple text files
- ✅ **Improved Error Handling**: Better error messages and recovery
- ✅ **Enhanced Logging**: Comprehensive logging system with file rotation
- ✅ **Modern Python**: Updated to use modern Python practices
- ✅ **Backup System**: Built-in data backup functionality
- ✅ **Better Performance**: Optimized download and upload processes
- ✅ **Admin Controls**: Enhanced admin commands and statistics

## 📋 Features

- **Download mega.nz links** without requiring a mega account
- **Support for files up to 5GB** (files larger than 2GB are split automatically)
- **Custom thumbnail and caption support** for uploads
- **Admin controls** for managing users and broadcasts
- **File-based storage** using simple text files (`users.txt`, `blacklist.txt`)
- **Improved error handling** and logging
- **Backup functionality** for data persistence
- **Concurrent download management** with limits
- **Progress tracking** during uploads and downloads

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- FFmpeg (for video processing)
- MEGAcmd or megatools (for downloading)

### Step 1: Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/mega-tg-updated.git
cd mega-tg-updated
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configuration
1. Copy `sample_config.py` to `config.py`:
```bash
cp sample_config.py config.py
```

2. Edit `config.py` and fill in your bot credentials:
```python
TG_BOT_TOKEN = "your_bot_token_here"
APP_ID = your_app_id
API_HASH = "your_api_hash"
OWNER_ID = your_telegram_id
```

### Step 4: Run the Bot
```bash
python bot.py
```

## 📱 Commands

### User Commands
- `/start` - Start the bot and get welcome message
- `/help` - Get detailed help guide
- `/about` - About the bot and features
- `/mythumbnail` - Show your current custom thumbnail
- `/deletethumbnail` - Delete your custom thumbnail
- `/captionhelp` - Help for caption feature

### Admin Commands (Owner Only)
- `/stats` - Get bot usage statistics
- `/broadcast` - Send message to all users
- `/backup` - Create data backup
- `/logs` - Get recent bot logs
- `/black <user_id>` - Blacklist a user
- `/unblack <user_id>` - Remove user from blacklist
- `/listblack` - List all blacklisted users
- `/clearblacklist` - Clear all blacklisted users (with confirmation)

## 🎯 Usage

### Basic Usage
1. Send a mega.nz link to the bot
2. The bot will process and download the file
3. Files larger than 2GB will be automatically split
4. The bot uploads the file(s) back to you

### Custom Thumbnails
1. Send a photo to the bot
2. The photo will be saved as your custom thumbnail
3. All future uploads will use this thumbnail

### Custom Captions
1. Forward any file to the bot or upload a file
2. Reply to that file with your desired caption
3. The bot will re-upload the file with your custom caption

## 📁 File Structure

```
mega-tg-updated/
├── bot.py                 # Main bot file
├── config.py             # Configuration (create from sample)
├── sample_config.py      # Configuration template
├── requirements.txt      # Python dependencies
├── translation.py        # Bot messages and text
├── database/
│   ├── __init__.py
│   ├── file_db.py       # File-based database handler
│   ├── userchats.py     # User management
│   └── blacklist.py     # Blacklist management
├── plugins/
│   ├── help_text.py     # Help and start commands
│   ├── megadl.py        # Main download functionality
│   ├── broadcast.py     # Admin broadcast features
│   ├── blacklist.py     # Blacklist management
│   ├── custom_thumbnail.py # Thumbnail handling
│   └── caption.py       # Caption functionality
├── helpers/
│   ├── download_uplaod_helper.py # Upload utilities
│   └── files_spliiting.py        # File splitting utilities
├── data/                # Bot data files (auto-created)
│   ├── users.txt
│   └── blacklist.txt
├── logs/                # Log files (auto-created)
└── backup/              # Backup files (auto-created)
```

## ⚙️ Configuration Options

### Required Settings
```python
TG_BOT_TOKEN = "your_bot_token"      # From @BotFather
APP_ID = your_app_id                 # From my.telegram.org
API_HASH = "your_api_hash"           # From my.telegram.org
OWNER_ID = your_telegram_id          # Your Telegram user ID
```

### Optional Settings
```python
AUTH_USERS = {user_id1, user_id2}    # Users with special privileges
Mega_email = "your_mega_email"       # For pro/business accounts
Mega_password = "your_mega_password" # For pro/business accounts
MAX_CONCURRENT_DOWNLOADS = 3         # Concurrent download limit
DOWNLOAD_TIMEOUT = 3600              # Download timeout in seconds
```

## 🔧 Deployment

### Local Deployment
```bash
python bot.py
```

### Using Screen (Linux)
```bash
screen -S megabot
python bot.py
# Press Ctrl+A then D to detach
```

### Using PM2
```bash
npm install -g pm2
pm2 start bot.py --name megabot --interpreter python3
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "bot.py"]
```

## 🐛 Troubleshooting

### Common Issues

1. **Bot not responding**
   - Check if bot token is correct
   - Verify API_ID and API_HASH
   - Check logs for errors

2. **Download failures**
   - Ensure MEGAcmd or megatools is installed
   - Check if mega.nz link is valid and not expired
   - Verify internet connection

3. **Upload failures**
   - Check file size (Telegram limit is 2GB per file)
   - Verify bot has necessary permissions
   - Check available disk space

### Log Files
Check the `logs/` directory for detailed error information:
```bash
tail -f logs/bot_YYYYMMDD.log
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the GPL-3.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original bot by [@XMYSTERlOUSX](https://github.com/XMYSTERlOUSX)
- [Pyrogram](https://github.com/pyrogram/pyrogram) for the Telegram Bot API
- [MEGAcmd](https://github.com/meganz/MEGAcmd) and [megatools](https://megatools.megous.com/) for download engines
- All contributors and users of this project

## 📞 Support

- Create an issue on GitHub for bug reports
- Join our Telegram group: [Your Group Link]
- Email: your-email@example.com

---

<p align="center">Made with ❤️ by the community</p>
