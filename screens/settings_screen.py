"""
Settings Screen - App configuration
"""

from kivy.uix.screenmanager import Screen
from kivy.app import App
from kivy.clock import Clock


class SettingsScreen(Screen):
    """
    Settings screen for app configuration
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def on_enter(self):
        """Called when screen becomes active"""
        self._load_settings()
    
    def _load_settings(self):
        """Load current settings into UI"""
        app = App.get_running_app()
        settings = app.settings
        
        # Theme
        theme = settings.get('theme', 'dark')
        if theme == 'dark':
            self.ids.theme_dark.state = 'down'
            self.ids.theme_light.state = 'normal'
        else:
            self.ids.theme_dark.state = 'normal'
            self.ids.theme_light.state = 'down'
        
        # TTS
        self.ids.tts_switch.active = settings.get('tts', False)
        
        # API URL
        api_url = settings.get('api_url', 'http://localhost:8000')
        self.ids.api_url_input.text = api_url
        
        # User info
        stats = app.stats
        self.ids.user_name.text = stats.get('userName', 'Tony Stark')
        level = self._calculate_level(stats.get('totalMessages', 0))
        self.ids.user_level.text = f'Level {level} Assistant Master'
    
    def _calculate_level(self, messages):
        """Calculate user level based on message count"""
        if messages < 10:
            return 1
        elif messages < 50:
            return 2
        elif messages < 100:
            return 3
        elif messages < 500:
            return 4
        elif messages < 1000:
            return 5
        else:
            return 6
    
    def set_theme(self, theme):
        """Set app theme"""
        app = App.get_running_app()
        app.settings['theme'] = theme
        self._apply_theme(theme)
    
    def _apply_theme(self, theme):
        """Apply theme to app"""
        # Theme colors would be applied here
        # For now, we just store the preference
        pass
    
    def set_tts(self, enabled):
        """Enable/disable text-to-speech"""
        app = App.get_running_app()
        app.settings['tts'] = enabled
    
    def save_settings(self):
        """Save all settings"""
        app = App.get_running_app()
        
        # Get API URL
        api_url = self.ids.api_url_input.text.strip()
        if api_url:
            app.settings['api_url'] = api_url
            app.api_service.base_url = api_url
        
        # Save to storage
        app.storage_service.save_settings(app.settings)
        
        # Show confirmation
        self._show_toast('Settings saved!')
        
        # Go back to chat
        Clock.schedule_once(lambda dt: self.go_back(), 0.5)
    
    def _show_toast(self, message):
        """Show a toast message"""
        # Simple toast implementation
        print(f"Toast: {message}")
    
    def go_back(self):
        """Return to chat screen"""
        self.manager.current = 'chat'
