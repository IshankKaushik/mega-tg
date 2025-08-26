from . import DB, get_stuff
import logging

logger = logging.getLogger(__name__)

def add_blacklist(user_id: int):
    """Add user to blacklist"""
    try:
        blacklist_data = get_stuff("blacklist")
        if not blacklist_data:
            blacklist_data = {"USERS": []}
        
        user_list = blacklist_data.get("USERS", [])
        user_id = int(user_id)
        
        if user_id not in user_list:
            user_list.append(user_id)
            blacklist_data["USERS"] = user_list
            DB.set("blacklist", blacklist_data)
            logger.info(f"Added user to blacklist: {user_id}")
            return True
        
        return False
    except Exception as e:
        logger.error(f"Error adding user {user_id} to blacklist: {e}")
        return False

def check_blacklist(user_id: int) -> bool:
    """Check if user is blacklisted"""
    try:
        blacklist_data = get_stuff("blacklist")
        if not blacklist_data or "USERS" not in blacklist_data:
            return False
        
        user_id = int(user_id)
        return user_id in blacklist_data["USERS"]
    except Exception as e:
        logger.error(f"Error checking blacklist for user {user_id}: {e}")
        return False

def remove_blacklist(user_id: int) -> str:
    """Remove user from blacklist"""
    try:
        blacklist_data = get_stuff("blacklist")
        if not blacklist_data or "USERS" not in blacklist_data:
            return "Blacklist is empty!"
        
        user_list = blacklist_data["USERS"]
        user_id = int(user_id)
        
        if user_id not in user_list:
            return "User was not blacklisted!"
        
        user_list.remove(user_id)
        blacklist_data["USERS"] = user_list
        DB.set("blacklist", blacklist_data)
        logger.info(f"Removed user from blacklist: {user_id}")
        return "Removed user from blacklist!"
        
    except Exception as e:
        logger.error(f"Error removing user {user_id} from blacklist: {e}")
        return f"Error removing user from blacklist: {e}"

def get_blacklisted():
    """Get all blacklisted user IDs"""
    try:
        blacklist_data = get_stuff("blacklist")
        if not blacklist_data or "USERS" not in blacklist_data:
            return []
        return blacklist_data["USERS"]
    except Exception as e:
        logger.error(f"Error getting blacklisted users: {e}")
        return []

def get_blacklist_count():
    """Get total number of blacklisted users"""
    try:
        return len(get_blacklisted())
    except Exception as e:
        logger.error(f"Error getting blacklist count: {e}")
        return 0
