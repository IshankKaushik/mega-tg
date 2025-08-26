from . import DB, get_stuff
import logging

logger = logging.getLogger(__name__)

def add_chat(user_id: int):
    """Add user to the users list"""
    try:
        users_data = get_stuff("users")
        if not users_data:
            users_data = {"USERS": []}
        
        user_list = users_data.get("USERS", [])
        
        # Convert to int to ensure consistency
        user_id = int(user_id)
        
        if user_id not in user_list:
            user_list.append(user_id)
            users_data["USERS"] = user_list
            DB.set("users", users_data)
            logger.info(f"Added new user: {user_id}")
        
    except Exception as e:
        logger.error(f"Error adding user {user_id}: {e}")

def get_all_chats():
    """Get all user IDs"""
    try:
        users_data = get_stuff("users")
        if not users_data or "USERS" not in users_data:
            return []
        return users_data["USERS"]
    except Exception as e:
        logger.error(f"Error getting all chats: {e}")
        return []

def remove_chat(user_id: int):
    """Remove user from the users list"""
    try:
        users_data = get_stuff("users")
        if not users_data or "USERS" not in users_data:
            return False
        
        user_list = users_data["USERS"]
        user_id = int(user_id)
        
        if user_id in user_list:
            user_list.remove(user_id)
            users_data["USERS"] = user_list
            DB.set("users", users_data)
            logger.info(f"Removed user: {user_id}")
            return True
        
        return False
    except Exception as e:
        logger.error(f"Error removing user {user_id}: {e}")
        return False

def get_user_count():
    """Get total number of users"""
    try:
        return len(get_all_chats())
    except Exception as e:
        logger.error(f"Error getting user count: {e}")
        return 0
