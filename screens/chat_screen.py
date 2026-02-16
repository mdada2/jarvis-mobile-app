"""
Chat Screen - Main chat interface
"""

from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty
from kivy.utils import get_color_from_hex
from datetime import datetime
import threading


class MessageBubble(BoxLayout):
    """A single message bubble in the chat"""
    is_user = BooleanProperty(False)
    message_text = StringProperty('')
    timestamp = StringProperty('')
    
    def __init__(self, text, is_user=False, **kwargs):
        super().__init__(**kwargs)
        self.is_user = is_user
        self.message_text = text
        self.timestamp = datetime.now().strftime('%I:%M %p')
        
        # Set colors based on sender
        if is_user:
            self.canvas.before.children[0].rgba = get_color_from_hex('#667eea')
        else:
            self.canvas.before.children[0].rgba = get_color_from_hex('#1a1a2e')


class ChatScreen(Screen):
    """
    Main chat screen with message input and display
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.messages = []
        self.is_processing = False
        
    def on_enter(self):
        """Called when screen becomes active"""
        # Load any saved session
        app = self.get_app()
        if app.session_id:
            self.load_session(app.session_id)
    
    def get_app(self):
        """Get the main app instance"""
        from kivy.app import App
        return App.get_running_app()
    
    def set_mode(self, mode):
        """Set chat mode (general or realtime)"""
        app = self.get_app()
        app.current_mode = mode
        self.ids.general_mode.state = 'down' if mode == 'general' else 'normal'
        self.ids.realtime_mode.state = 'down' if mode == 'realtime' else 'normal'
    
    def send_message(self):
        """Send a message to the AI"""
        if self.is_processing:
            return
            
        input_field = self.ids.message_input
        message = input_field.text.strip()
        
        if not message:
            return
        
        # Clear input
        input_field.text = ''
        
        # Add user message to UI
        self.add_message(message, is_user=True)
        
        # Process in background
        self.is_processing = True
        self.ids.send_btn.disabled = True
        self.ids.send_btn.text = '...'
        
        thread = threading.Thread(target=self._process_message, args=(message,))
        thread.daemon = True
        thread.start()
    
    def _process_message(self, message):
        """Process message in background thread"""
        try:
            app = self.get_app()
            
            # Call API
            response = app.api_service.send_message(
                message=message,
                session_id=app.session_id,
                mode=app.current_mode
            )
            
            # Update session ID if new
            if response.get('session_id'):
                app.session_id = response['session_id']
            
            # Get AI response
            ai_response = response.get('response', 'Sorry, I could not process that.')
            
            # Update UI on main thread
            Clock.schedule_once(lambda dt: self._handle_response(ai_response), 0)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            Clock.schedule_once(lambda dt: self._handle_response(error_msg), 0)
    
    def _handle_response(self, response):
        """Handle AI response on main thread"""
        self.add_message(response, is_user=False)
        self.is_processing = False
        self.ids.send_btn.disabled = False
        self.ids.send_btn.text = 'Send'
        
        # Speak response if TTS enabled
        app = self.get_app()
        if app.settings.get('tts', False):
            app.voice_service.speak(response)
        
        # Update stats
        app.stats['total_messages'] = app.stats.get('total_messages', 0) + 2
        app.storage_service.save_stats(app.stats)
    
    def add_message(self, text, is_user=False):
        """Add a message bubble to the chat"""
        container = self.ids.messages_container
        
        # Create message bubble
        bubble = MessageBubble(text=text, is_user=is_user)
        bubble.size_hint_x = 0.85 if not is_user else 0.85
        bubble.pos_hint = {'right': 1} if is_user else {'x': 0}
        
        container.add_widget(bubble)
        
        # Store message
        self.messages.append({
            'text': text,
            'is_user': is_user,
            'timestamp': datetime.now().isoformat()
        })
        
        # Scroll to bottom
        Clock.schedule_once(lambda dt: self._scroll_to_bottom(), 0.1)
    
    def _scroll_to_bottom(self):
        """Scroll the message view to the bottom"""
        scroll_view = self.ids.scroll_view
        scroll_view.scroll_y = 0
    
    def toggle_voice(self):
        """Toggle voice input"""
        app = self.get_app()
        
        if app.voice_service.is_listening:
            app.voice_service.stop_listening()
            self.ids.voice_btn.text = '🎤'
        else:
            app.voice_service.start_listening(self._on_voice_result)
            self.ids.voice_btn.text = '🔴'
    
    def _on_voice_result(self, text):
        """Callback when voice input is received"""
        self.ids.message_input.text = text
        self.ids.voice_btn.text = '🎤'
    
    def open_settings(self):
        """Open settings screen"""
        self.manager.current = 'settings'
    
    def open_history(self):
        """Open history screen"""
        self.manager.current = 'history'
    
    def load_session(self, session_id):
        """Load a previous chat session"""
        app = self.get_app()
        
        try:
            history = app.api_service.get_history(session_id)
            
            # Clear current messages
            self.clear_messages()
            
            # Add historical messages
            for msg in history.get('messages', []):
                self.add_message(
                    msg.get('content', ''),
                    is_user=msg.get('role') == 'user'
                )
        except Exception as e:
            print(f"Error loading session: {e}")
    
    def clear_messages(self):
        """Clear all messages from the chat"""
        container = self.ids.messages_container
        
        # Keep only the welcome label
        while len(container.children) > 1:
            container.remove_widget(container.children[0])
        
        self.messages = []
    
    def new_chat(self):
        """Start a new chat session"""
        app = self.get_app()
        app.session_id = None
        self.clear_messages()
