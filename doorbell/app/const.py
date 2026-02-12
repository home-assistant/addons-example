import os

APP_PORT = 5000
AUDIO_DIR = "audio-files/"
ALLOWED_EXTENSIONS = {".mp3",".wav",".ogg"}
TTS_FILE = "tts.wav"
BEEP_FILE = "beep.wav"
ADDON_SLUG = "doorbell"

#HOST      = os.getenv("API_HOST", "0.0.0.0")
PORT      = APP_PORT
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
TTS_LANG  = os.getenv("TTS_LANG", "en-US")
MAX_LOOP_SEC  = os.getenv("LOOP_DURATION", "60")

HOST = "0.0.0.0"

# Disable ALSA warning spam
os.environ["ALSA_LOG_LEVEL"] = "none"