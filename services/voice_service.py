"""
Voice Service - Speech recognition and text-to-speech
"""

from kivy.utils import platform
from kivy.clock import Clock
import threading


class VoiceService:
    """
    Handles speech recognition and text-to-speech
    Works on Android and desktop platforms
    """
    
    def __init__(self):
        self.is_listening = False
        self._callback = None
        self._tts_engine = None
        self._recognizer = None
        
        # Initialize platform-specific services
        self._init_tts()
        self._init_recognizer()
    
    def _init_tts(self):
        """Initialize text-to-speech engine"""
        if platform == 'android':
            self._init_android_tts()
        else:
            self._init_desktop_tts()
    
    def _init_android_tts(self):
        """Initialize Android TTS using pyjnius"""
        try:
            from jnius import autoclass
            
            Locale = autoclass('java.util.Locale')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
            
            self._tts_engine = TextToSpeech(
                PythonActivity.mActivity,
                None
            )
            self._tts_engine.setLanguage(Locale.US)
            
        except Exception as e:
            print(f"Failed to initialize Android TTS: {e}")
            self._tts_engine = None
    
    def _init_desktop_tts(self):
        """Initialize desktop TTS using pyttsx3"""
        try:
            import pyttsx3
            self._tts_engine = pyttsx3.init()
            
            # Configure voice
            voices = self._tts_engine.getProperty('voices')
            if voices:
                # Try to find a good English voice
                for voice in voices:
                    if 'english' in voice.name.lower() or 'en' in voice.id.lower():
                        self._tts_engine.setProperty('voice', voice.id)
                        break
            
            self._tts_engine.setProperty('rate', 150)
            
        except Exception as e:
            print(f"Failed to initialize desktop TTS: {e}")
            self._tts_engine = None
    
    def _init_recognizer(self):
        """Initialize speech recognizer"""
        if platform == 'android':
            self._init_android_recognizer()
        else:
            self._init_desktop_recognizer()
    
    def _init_android_recognizer(self):
        """Initialize Android speech recognizer"""
        # Android recognizer is initialized on-demand
        pass
    
    def _init_desktop_recognizer(self):
        """Initialize desktop speech recognizer"""
        try:
            import speech_recognition as sr
            self._recognizer = sr.Recognizer()
        except Exception as e:
            print(f"Failed to initialize speech recognizer: {e}")
            self._recognizer = None
    
    def start_listening(self, callback):
        """
        Start listening for voice input
        
        Args:
            callback: Function to call with recognized text
        """
        self.is_listening = True
        self._callback = callback
        
        if platform == 'android':
            self._start_android_listening()
        else:
            self._start_desktop_listening()
    
    def _start_android_listening(self):
        """Start Android speech recognition"""
        try:
            from jnius import autoclass
            
            Intent = autoclass('android.content.Intent')
            RecognizerIntent = autoclass('android.speech.RecognizerIntent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            
            intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, 
                          RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, 'en-US')
            intent.putExtra(RecognizerIntent.EXTRA_PROMPT, 'Speak to J.A.R.V.I.S...')
            
            PythonActivity.mActivity.startActivityForResult(intent, 1234)
            
        except Exception as e:
            print(f"Failed to start Android speech recognition: {e}")
            self.stop_listening()
    
    def _start_desktop_listening(self):
        """Start desktop speech recognition"""
        if not self._recognizer:
            self.stop_listening()
            return
        
        def listen_thread():
            try:
                import speech_recognition as sr
                
                with sr.Microphone() as source:
                    self._recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self._recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                try:
                    text = self._recognizer.recognize_google(audio)
                    if self._callback:
                        Clock.schedule_once(lambda dt: self._callback(text), 0)
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print(f"Speech recognition error: {e}")
                    
            except Exception as e:
                print(f"Listening error: {e}")
            finally:
                Clock.schedule_once(lambda dt: self.stop_listening(), 0)
        
        thread = threading.Thread(target=listen_thread)
        thread.daemon = True
        thread.start()
    
    def stop_listening(self):
        """Stop listening for voice input"""
        self.is_listening = False
    
    def speak(self, text):
        """
        Speak text using TTS
        
        Args:
            text: Text to speak
        """
        if not self._tts_engine:
            return
        
        if platform == 'android':
            self._speak_android(text)
        else:
            self._speak_desktop(text)
    
    def _speak_android(self, text):
        """Speak using Android TTS"""
        try:
            from jnius import autoclass
            TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
            
            if self._tts_engine:
                self._tts_engine.speak(
                    text,
                    TextToSpeech.QUEUE_FLUSH,
                    None
                )
        except Exception as e:
            print(f"Android TTS error: {e}")
    
    def _speak_desktop(self, text):
        """Speak using desktop TTS"""
        try:
            if self._tts_engine:
                self._tts_engine.say(text)
                self._tts_engine.runAndWait()
        except Exception as e:
            print(f"Desktop TTS error: {e}")
    
    def stop_speaking(self):
        """Stop any ongoing speech"""
        if platform == 'android' and self._tts_engine:
            try:
                self._tts_engine.stop()
            except:
                pass
        elif self._tts_engine:
            try:
                self._tts_engine.stop()
            except:
                pass
