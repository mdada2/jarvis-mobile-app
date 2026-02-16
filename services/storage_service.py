"""
Storage Service - Local data persistence
"""

import json
import os
from typing import Dict, Any, List
from kivy.utils import platform


class StorageService:
    """
    Handles local storage for settings, stats, and sessions
    Uses JSON files for persistence
    """
    
    def __init__(self):
        self._storage_dir = self._get_storage_dir()
        self._ensure_storage_dir()
    
    def _get_storage_dir(self) -> str:
        """Get the appropriate storage directory for the platform"""
        if platform == 'android':
            # On Android, use the app's private storage
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            return context.getFilesDir().getPath()
        else:
            # On desktop, use a local directory
            return os.path.join(os.path.dirname(__file__), '..', 'storage')
    
    def _ensure_storage_dir(self):
        """Ensure the storage directory exists"""
        if not os.path.exists(self._storage_dir):
            os.makedirs(self._storage_dir)
    
    def _get_file_path(self, filename: str) -> str:
        """Get full path for a storage file"""
        return os.path.join(self._storage_dir, filename)
    
    def _read_json(self, filename: str) -> Dict[str, Any]:
        """Read JSON file"""
        filepath = self._get_file_path(filename)
        
        if not os.path.exists(filepath):
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return {}
    
    def _write_json(self, filename: str, data: Dict[str, Any]) -> bool:
        """Write JSON file"""
        filepath = self._get_file_path(filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error writing {filename}: {e}")
            return False
    
    # Settings
    def load_settings(self) -> Dict[str, Any]:
        """Load app settings"""
        defaults = {
            'theme': 'dark',
            'color_scheme': 'purple',
            'font_size': 'medium',
            'tts': False,
            'api_url': 'http://localhost:8000',
            'notifications': True,
            'auto_save': True
        }
        
        saved = self._read_json('settings.json')
        return {**defaults, **saved}
    
    def save_settings(self, settings: Dict[str, Any]) -> bool:
        """Save app settings"""
        return self._write_json('settings.json', settings)
    
    # Stats
    def load_stats(self) -> Dict[str, Any]:
        """Load user stats"""
        defaults = {
            'total_messages': 0,
            'exported_count': 0,
            'last_login': None,
            'streak': 0,
            'userName': 'Tony Stark'
        }
        
        saved = self._read_json('stats.json')
        return {**defaults, **saved}
    
    def save_stats(self, stats: Dict[str, Any]) -> bool:
        """Save user stats"""
        return self._write_json('stats.json', stats)
    
    # Sessions
    def load_sessions(self) -> List[Dict[str, Any]]:
        """Load saved chat sessions"""
        data = self._read_json('sessions.json')
        return data.get('sessions', [])
    
    def save_sessions(self, sessions: List[Dict[str, Any]]) -> bool:
        """Save chat sessions"""
        return self._write_json('sessions.json', {'sessions': sessions})
    
    def save_session(self, session: Dict[str, Any]) -> bool:
        """Save a single session"""
        sessions = self.load_sessions()
        
        # Update or add session
        session_id = session.get('session_id')
        found = False
        
        for i, s in enumerate(sessions):
            if s.get('session_id') == session_id:
                sessions[i] = session
                found = True
                break
        
        if not found:
            sessions.insert(0, session)
        
        return self.save_sessions(sessions)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        sessions = self.load_sessions()
        sessions = [s for s in sessions if s.get('session_id') != session_id]
        return self.save_sessions(sessions)
    
    # Messages
    def load_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Load messages for a session"""
        data = self._read_json(f'messages_{session_id}.json')
        return data.get('messages', [])
    
    def save_messages(self, session_id: str, messages: List[Dict[str, Any]]) -> bool:
        """Save messages for a session"""
        return self._write_json(f'messages_{session_id}.json', {'messages': messages})
    
    # Clear all data
    def clear_all(self) -> bool:
        """Clear all stored data"""
        try:
            for filename in os.listdir(self._storage_dir):
                if filename.endswith('.json'):
                    os.remove(os.path.join(self._storage_dir, filename))
            return True
        except Exception as e:
            print(f"Error clearing data: {e}")
            return False
