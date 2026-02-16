# J.A.R.V.I.S Mobile App

A Kivy-based Android application that connects to the J.A.R.V.I.S AI backend.

## Features

- 💬 **Chat Interface**: Clean, modern chat UI with message bubbles
- 🎤 **Voice Input**: Speech-to-text for hands-free messaging
- 🔊 **Text-to-Speech**: AI responses can be read aloud
- 📱 **Dark Theme**: Eye-friendly dark mode design
- 📜 **Chat History**: View and resume previous conversations
- ⚙️ **Settings**: Customize app behavior and API endpoint
- 🔄 **Dual Mode**: General chat and Realtime (web search) modes

## Project Structure

```
mobile_app/
├── main.py              # App entry point
├── jarvis.kv            # Kivy UI definitions
├── buildozer.spec       # APK build configuration
├── requirements.txt     # Python dependencies
├── screens/
│   ├── __init__.py
│   ├── chat_screen.py   # Main chat interface
│   ├── settings_screen.py
│   └── history_screen.py
└── services/
    ├── __init__.py
    ├── api_service.py   # Backend communication
    ├── voice_service.py # Speech recognition & TTS
    └── storage_service.py # Local data persistence
```

## Prerequisites

### For Desktop Testing
- Python 3.8+
- Kivy 2.2.0+

### For APK Building
- Linux (Ubuntu/Debian recommended) or WSL2 on Windows
- Buildozer
- Android SDK/NDK (automatically installed by buildozer)

## Installation

### Desktop Testing

1. Create a virtual environment:
```bash
cd mobile_app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
python main.py
```

### Building APK (Linux/WSL2)

1. Install buildozer:
```bash
pip install buildozer
```

2. Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev automake
```

3. Build the APK:
```bash
cd mobile_app
buildozer android debug
```

4. The APK will be in the `bin/` directory.

### Building on Windows

Since buildozer doesn't work natively on Windows, you have two options:

#### Option 1: WSL2 (Recommended)
1. Install WSL2 with Ubuntu
2. Follow the Linux instructions above

#### Option 2: Google Colab
1. Upload the `mobile_app` folder to Google Drive
2. Open a new Colab notebook
3. Run the following:

```python
!pip install buildozer
!apt update
!apt install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev automake

# Upload your mobile_app folder
from google.colab import drive
drive.mount('/content/drive')

%cd /content/drive/MyDrive/mobile_app
!buildozer android debug
```

## Configuration

### Backend URL
By default, the app connects to `http://localhost:8000`. To change this:

1. Open the app
2. Go to Settings
3. Enter your backend URL (e.g., `https://your-vercel-app.vercel.app`)
4. Save settings

### Deploying Backend
The backend must be deployed and accessible from the internet. Options:
- **Vercel**: Already configured with `vercel.json`
- **Railway**: Simple deployment
- **Render**: Free tier available
- **Self-hosted**: Use ngrok for local testing

## Permissions

The app requires these Android permissions:
- `INTERNET`: For API communication
- `RECORD_AUDIO`: For voice input
- `WRITE_EXTERNAL_STORAGE`: For saving chat history
- `READ_EXTERNAL_STORAGE`: For reading saved data

## Troubleshooting

### Build Errors
1. Clean build: `buildozer android clean`
2. Delete `.buildozer` folder and rebuild
3. Check Java version: `java -version` (should be 17)

### Runtime Errors
1. Check logcat: `buildozer android debug deploy run logcat`
2. Ensure backend URL is correct
3. Check network connectivity

### Voice Not Working
- Ensure microphone permission is granted
- On Android 12+, grant microphone permission manually

## Development

### Adding New Features
1. Create new screen in `screens/`
2. Add service logic in `services/`
3. Update `main.py` to register screen
4. Add UI in `jarvis.kv`

### Testing
```bash
# Run with debug output
KIVY_LOG_MODE=PYTHON python main.py
```

## License

This project is for personal use. Feel free to modify and distribute.

## Credits

- Built with [Kivy](https://kivy.org/)
- Powered by [Groq](https://groq.com/)
- Inspired by J.A.R.V.I.S from Iron Man
