import os

class Config(object):
    # Telegram Bot Configuration
    TG_BOT_TOKEN = os.environ.get("TG_BOT_TOKEN", "") # Make a bot from https://t.me/BotFather and enter the token here
    #If deploying on vps edit the above value as example := TG_BOT_TOKEN = "Your-bot-token-inside-inverted-commas."
    
    APP_ID = int(os.environ.get("APP_ID", 12345)) # Get this value from https://my.telegram.org/apps
    #If deploying on vps edit the above value as example := APP_ID = Your-APP_ID-without-inverted-commas
    
    API_HASH = os.environ.get("API_HASH", "") # Get this value from https://my.telegram.org/apps
    #If deploying on vps edit the above value as example := API_HASH = "Your-API_HASH-inside-inverted-commas."
    
    # Mega.nz Configuration (Optional - for pro/business features)
    Mega_email = os.environ.get("Mega_email", "None") # This is not necessary! Enter your mega email only if you have a mega.nz account with pro/business features.
    #If deploying on vps edit the above value as example := Mega_email = "Your-Mega_email-inside-inverted-commas."
    
    Mega_password = os.environ.get("Mega_password", "None") # This is not necessary! Enter your mega password only if you have a mega.nz account with pro/business features.
    #If deploying on vps edit the above value as example := Mega_password = "Your-Mega_password-inside-inverted-commas."
    
    # Bot Configuration
    Bot_username = os.environ.get("Bot_username", "") # Your bot's telegram username (must enter with '@' in the front of the username)
    #If deploying on vps edit the above value as example := Bot_username = "Your-Bot_username-inside-inverted-commas."
    
    OWNER_ID = os.environ.get("OWNER_ID", None) # Your(owner's) telegram id
    #If deploying on vps edit the above value as example := OWNER_ID = Your-telegram id-without-inverted-commas
    
    # Authorized Users Configuration
    AUTH_USERS = set(int(x) for x in os.environ.get("AUTH_USERS", "").split() if x.strip()) # Id's of the telegram users, who you want to allow for multitasking - downloading multiple links at once!
    
    #If deploying on heroku separate the ids by space. (don't put commas. Only separate each of the id's with space)
    
    #If deploying on vps edit the above value as example := 
    #AUTH_USERS = set(int(x) for x in (id1, id2)) 👈 Type exactly as that and replace id1 and id2 with the id's of the telegram users, who you want to allow for multitasking. You can add many users like that!
    
    # Directory Configuration
    DOWNLOAD_LOCATION = "./DOWNLOADS" # The download location for users. (Don't change anything in this field!)
    ADMIN_LOCATION = "./ADOWNLOADS" # The download location for auth users. (Don't change anything in this field!)
    CREDENTIALS_LOCATION = "./CREDENTIALS" # Location where your mega.nz credentials for megatools gets saved if you provide them. (Don't change anything in this field!)
    DATA_LOCATION = "./data" # Location where bot data files are stored (users.txt, blacklist.txt, etc.)
    
    # File Size Limits
    MAX_FILE_SIZE = 2040108421  # ~2GB in bytes (Telegram limit)
    SPLIT_SIZE = 2040108421     # Size to split large files
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = os.environ.get("LOG_FILE", "bot.log")
    
    # Performance Configuration
    MAX_CONCURRENT_DOWNLOADS = int(os.environ.get("MAX_CONCURRENT_DOWNLOADS", 3))
    DOWNLOAD_TIMEOUT = int(os.environ.get("DOWNLOAD_TIMEOUT", 3600))  # 1 hour
    
    # Feature Flags
    ENABLE_BACKUP = os.environ.get("ENABLE_BACKUP", "True").lower() == "true"
    BACKUP_INTERVAL = int(os.environ.get("BACKUP_INTERVAL", 86400))  # 24 hours
