import json
import os
import threading
from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)

class FileDB:
    """Simple file-based database using JSON text files"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.lock = threading.Lock()
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        # Initialize default files
        self._init_files()
    
    def _init_files(self):
        """Initialize default data files"""
        default_files = {
            "users.txt": {"USERS": []},
            "blacklist.txt": {"USERS": []},
            "settings.txt": {}
        }
        
        for filename, default_data in default_files.items():
            filepath = os.path.join(self.data_dir, filename)
            if not os.path.exists(filepath):
                self._write_file(filepath, default_data)
    
    def _read_file(self, filepath: str) -> Dict[str, Any]:
        """Read and parse JSON from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Error reading {filepath}: {e}")
            return {}
    
    def _write_file(self, filepath: str, data: Dict[str, Any]):
        """Write JSON data to file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error writing to {filepath}: {e}")
            raise
    
    def get(self, key: str) -> Dict[str, Any]:
        """Get data from file"""
        filepath = os.path.join(self.data_dir, f"{key.lower()}.txt")
        with self.lock:
            return self._read_file(filepath)
    
    def set(self, key: str, data: Dict[str, Any]):
        """Set data to file"""
        filepath = os.path.join(self.data_dir, f"{key.lower()}.txt")
        with self.lock:
            self._write_file(filepath, data)
    
    def update(self, key: str, data: Dict[str, Any]):
        """Update existing data in file"""
        with self.lock:
            current_data = self.get(key)
            current_data.update(data)
            self.set(key, current_data)
    
    def backup(self, backup_dir: str = "backup"):
        """Create backup of all data files"""
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}")
        
        try:
            shutil.copytree(self.data_dir, backup_path)
            logger.info(f"Backup created at {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            raise

# Global database instance
DB = FileDB()

def get_stuff(key: str) -> Dict[str, Any]:
    """Get data from file database"""
    return DB.get(key)
