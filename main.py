"""
J.A.R.V.I.S Mobile App - Main Entry Point
==========================================
A Kivy-based mobile application that connects to the J.A.R.V.I.S backend.
"""

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from kivy.utils import platform

# Set window size for desktop testing
if platform != 'android':
    Window.size = (400, 700)

from screens.chat_screen import ChatScreen
from screens.settings_screen import SettingsScreen
from screens.history_screen import HistoryScreen
from services.api_service import APIService
from services.voice_service import VoiceService
from services.storage_service import StorageService


class JarvisApp(App):
    """
    Main Application Class
    Manages screens, services, and app lifecycle
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize services
        self.api_service = APIService()
        self.voice_service = VoiceService()
        self.storage_service = StorageService()
        
        # App state
        self.session_id = None
        self.current_mode = 'general'  # 'general' or 'realtime'
        self.settings = self.storage_service.load_settings()
        self.stats = self.storage_service.load_stats()
    
    def build(self):
        """
        Build the app UI
        Returns: ScreenManager with all screens
        """
        self.title = 'J.A.R.V.I.S'
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add screens
        sm.add_widget(ChatScreen(name='chat'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(HistoryScreen(name='history'))
        
        # Apply saved theme
        self.apply_theme()
        
        return sm
    
    def apply_theme(self):
        """Apply theme settings from storage"""
        theme = self.settings.get('theme', 'dark')
        # Theme will be applied via KV file
        
    def get_chat_screen(self):
        """Get reference to chat screen"""
        return self.root.get_screen('chat')
    
    def get_settings_screen(self):
        """Get reference to settings screen"""
        return self.root.get_screen('settings')
    
    def get_history_screen(self):
        """Get reference to history screen"""
        return self.root.get_screen('history')
    
    def on_stop(self):
        """Save data when app closes"""
        self.storage_service.save_settings(self.settings)
        self.storage_service.save_stats(self.stats)


if __name__ == '__main__':
    JarvisApp().run()
