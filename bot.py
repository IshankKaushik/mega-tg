import logging
import os
import sys
from datetime import datetime

# Configure logging
def setup_logging():
    """Setup logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set pyrogram logging level to WARNING to reduce noise
    logging.getLogger("pyrogram").setLevel(logging.WARNING)
    logging.getLogger("pyrogram.session").setLevel(logging.WARNING)
    logging.getLogger("pyrogram.connection").setLevel(logging.WARNING)

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)

# Import configuration
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    try:
        from config import Config
    except ImportError:
        logger.error("config.py not found! Please create config.py from sample_config.py")
        sys.exit(1)

# Import pyrogram
import pyrogram
from pyrogram import Client, idle

def create_directories():
    """Create essential directories if they don't exist"""
    directories = [
        Config.DOWNLOAD_LOCATION,
        Config.ADMIN_LOCATION,
        Config.CREDENTIALS_LOCATION,
        Config.DATA_LOCATION,
        "logs",
        "backup"
    ]
    
    for directory in directories:
        if not os.path.isdir(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")

def validate_config():
    """Validate essential configuration"""
    required_configs = {
        'TG_BOT_TOKEN': Config.TG_BOT_TOKEN,
        'APP_ID': Config.APP_ID,
        'API_HASH': Config.API_HASH,
        'OWNER_ID': Config.OWNER_ID
    }
    
    missing_configs = []
    for key, value in required_configs.items():
        if not value or (isinstance(value, str) and value.strip() == ""):
            missing_configs.append(key)
    
    if missing_configs:
        logger.error(f"Missing required configuration: {', '.join(missing_configs)}")
        logger.error("Please check your config.py file")
        sys.exit(1)
    
    logger.info("Configuration validation passed")

def setup_database():
    """Initialize database"""
    try:
        from database.file_db import DB
        logger.info("Database initialized successfully")
        
        # Create backup if enabled
        if Config.ENABLE_BACKUP:
            try:
                backup_path = DB.backup()
                logger.info(f"Initial backup created at: {backup_path}")
            except Exception as e:
                logger.warning(f"Failed to create initial backup: {e}")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

def main():
    """Main function to start the bot"""
    try:
        logger.info("Starting Mega Link Downloader Bot...")
        
        # Validate configuration
        validate_config()
        
        # Create essential directories
        create_directories()
        
        # Setup database
        setup_database()
        
        # Configure plugins
        plugins = dict(root="plugins")
        
        # Create pyrogram client
        app = Client(
            "Mega_Link_Downloader_Bot",
            bot_token=Config.TG_BOT_TOKEN,
            api_id=Config.APP_ID,
            api_hash=Config.API_HASH,
            plugins=plugins,
            workdir="."
        )
        
        logger.info("Bot configuration completed successfully")
        logger.info(f"Bot username: {Config.Bot_username}")
        logger.info(f"Owner ID: {Config.OWNER_ID}")
        logger.info(f"Auth users: {len(Config.AUTH_USERS)}")
        
        # Start the bot
        logger.info("Starting bot...")
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        logger.info("Bot shutdown completed")

if __name__ == "__main__":
    main()
