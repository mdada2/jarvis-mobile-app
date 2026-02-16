"""
History Screen - Chat history management
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.app import App
from kivy.properties import StringProperty
from datetime import datetime
import os
import json


class HistoryItem(BoxLayout):
    """A single history item in the list"""
    session_id = StringProperty('')
    preview = StringProperty('')
    date_str = StringProperty('')
    
    def __init__(self, session_id, preview, date_str, on_select=None, **kwargs):
        super().__init__(**kwargs)
        self.session_id = session_id
        self.preview = preview
        self.date_str = date_str
        self.on_select = on_select
        
        # Add touch handling
        self.bind(on_touch_down=self._on_touch)
    
    def _on_touch(self, instance, touch):
        if self.collide_point(*touch.pos):
            if self.on_select:
                self.on_select(self.session_id)
            return True
        return False


class HistoryScreen(Screen):
    """
    Screen for viewing and managing chat history
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.history_data = []
    
    def on_enter(self):
        """Called when screen becomes active"""
        self._load_history()
    
    def _load_history(self):
        """Load chat history from storage"""
        app = App.get_running_app()
        
        # Try to load from API first
        try:
            sessions = app.api_service.get_all_sessions()
            self._display_sessions(sessions)
        except Exception as e:
            print(f"Error loading from API: {e}")
            # Fall back to local storage
            self._load_local_history()
    
    def _load_local_history(self):
        """Load history from local storage"""
        app = App.get_running_app()
        sessions = app.storage_service.load_sessions()
        self._display_sessions(sessions)
    
    def _display_sessions(self, sessions):
        """Display sessions in the history list"""
        container = self.ids.history_container
        
        # Clear existing items
        container.clear_widgets()
        
        if not sessions:
            # Show empty state
            empty_label = Label(
                text='No chat history yet',
                size_hint_y=None,
                height='100dp',
                color=get_color_from_hex('#888888')
            )
            container.add_widget(empty_label)
            return
        
        # Add session items
        for session in sessions:
            item = HistoryItem(
                session_id=session.get('session_id', ''),
                preview=session.get('preview', 'No preview'),
                date_str=self._format_date(session.get('timestamp')),
                on_select=self._on_session_select
            )
            container.add_widget(item)
    
    def _format_date(self, timestamp):
        """Format timestamp for display"""
        if not timestamp:
            return 'Unknown'
        
        try:
            if isinstance(timestamp, str):
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = datetime.fromtimestamp(timestamp)
            
            now = datetime.now()
            diff = now - dt
            
            if diff.days == 0:
                return 'Today'
            elif diff.days == 1:
                return 'Yesterday'
            elif diff.days < 7:
                return f'{diff.days} days ago'
            else:
                return dt.strftime('%b %d, %Y')
        except:
            return 'Unknown'
    
    def _on_session_select(self, session_id):
        """Handle session selection"""
        app = App.get_running_app()
        app.session_id = session_id
        
        # Go back to chat and load session
        self.manager.current = 'chat'
        chat_screen = self.manager.get_screen('chat')
        chat_screen.load_session(session_id)
    
    def search_history(self, query):
        """Search through chat history"""
        query = query.lower().strip()
        
        if not query:
            self._load_history()
            return
        
        # Filter sessions
        filtered = []
        for session in self.history_data:
            preview = session.get('preview', '').lower()
            if query in preview:
                filtered.append(session)
        
        self._display_sessions(filtered)
    
    def new_chat(self):
        """Start a new chat session"""
        app = App.get_running_app()
        app.session_id = None
        
        # Go to chat screen
        self.manager.current = 'chat'
        chat_screen = self.manager.get_screen('chat')
        chat_screen.new_chat()
    
    def go_back(self):
        """Return to chat screen"""
        self.manager.current = 'chat'
    
    def delete_session(self, session_id):
        """Delete a chat session"""
        app = App.get_running_app()
        
        try:
            app.api_service.delete_session(session_id)
        except:
            pass
        
        # Remove from local storage
        app.storage_service.delete_session(session_id)
        
        # Refresh the list
        self._load_history()
