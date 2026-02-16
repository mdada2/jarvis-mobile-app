"""
API Service - Backend communication
"""

import requests
import json
from typing import Optional, Dict, Any, List


class APIService:
    """
    Handles all API communication with the J.A.R.V.I.S backend
    """
    
    def __init__(self, base_url: str = 'http://localhost:8000'):
        self.base_url = base_url
        self.timeout = 60  # seconds
        
    def set_base_url(self, url: str):
        """Update the base URL"""
        self.base_url = url.rstrip('/')
    
    def _get_url(self, endpoint: str) -> str:
        """Get full URL for an endpoint"""
        return f"{self.base_url}{endpoint}"
    
    def send_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        mode: str = 'general'
    ) -> Dict[str, Any]:
        """
        Send a message to the AI
        
        Args:
            message: The user's message
            session_id: Optional session ID for conversation continuity
            mode: 'general' or 'realtime'
        
        Returns:
            Dict with response and session_id
        """
        endpoint = '/chat' if mode == 'general' else '/chat/realtime'
        
        payload = {
            'message': message
        }
        
        if session_id:
            payload['session_id'] = session_id
        
        try:
            response = requests.post(
                self._get_url(endpoint),
                json=payload,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            return {
                'response': 'Sorry, the request timed out. Please try again.',
                'session_id': session_id
            }
        except requests.exceptions.ConnectionError:
            return {
                'response': 'Cannot connect to the server. Please check your connection.',
                'session_id': session_id
            }
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                return {
                    'response': "You've reached your daily API limit. Please try again later.",
                    'session_id': session_id
                }
            return {
                'response': f'Server error: {e.response.status_code}',
                'session_id': session_id
            }
        except Exception as e:
            return {
                'response': f'An error occurred: {str(e)}',
                'session_id': session_id
            }
    
    def get_history(self, session_id: str) -> Dict[str, Any]:
        """
        Get chat history for a session
        
        Args:
            session_id: The session ID
        
        Returns:
            Dict with messages list
        """
        try:
            response = requests.get(
                self._get_url(f'/chat/history/{session_id}'),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"Error getting history: {e}")
            return {'messages': []}
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """
        Get all chat sessions
        
        Returns:
            List of session objects
        """
        try:
            response = requests.get(
                self._get_url('/chat/sessions'),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json().get('sessions', [])
            
        except Exception as e:
            print(f"Error getting sessions: {e}")
            return []
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a chat session
        
        Args:
            session_id: The session ID to delete
        
        Returns:
            True if successful
        """
        try:
            response = requests.delete(
                self._get_url(f'/chat/session/{session_id}'),
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return True
            
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check server health status
        
        Returns:
            Health status dict
        """
        try:
            response = requests.get(
                self._get_url('/health'),
                timeout=10
            )
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
