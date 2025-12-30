import uvicorn
import logging
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, field_validator
import threading
from pico2wave import PicoTTS, VOICES
from beepnoise import BeepNoise
import beepnoise2
import wave
from io import BytesIO

# import your AudioPlayer class here
from audio_player import AudioPlayer

from const import LOG_LEVEL, HOST, PORT, ADDON_SLUG, TTS_LANG
from const import AUDIO_DIR, ALLOWED_EXTENSIONS

app = FastAPI(title="Doorbell API")

logging.basicConfig(level=LOG_LEVEL)

_LOGGER = logging.getLogger(__name__)

player_lock = threading.Lock()
player = None

#HOST = "0.0.0.0"
#PORT = 5000
#TTS_LANG = "de-DE"

favicon_path = 'favicon.ico'  # Adjust path to file


class PlayRequest(BaseModel):
    filename: str            # file path
    volume: int = 100

    @field_validator('volume')
    def validate_volume(cls, v):
        if v > 100 or v < 0:
            raise ValueError('Volume must between 0 and 100')
        return v

class LoopRequest(BaseModel):
    filename: str            # file path
    volume: int = 100

    @field_validator('volume')
    def validate_volume(cls, v):
        if v > 100 or v < 0:
            raise ValueError('Volume must between 0 and 100')
        return v

class BeepRequest(BaseModel):
    number: int = 1 # file path
    volume: int = 100

    @field_validator('volume')
    def validate_volume(cls, v):
        if v > 100 or v < 0:
            raise ValueError('Volume must between 0 and 100')
        return v

    @field_validator('number')
    def validate_number(cls, v):
        if v > 10 or v < 1:
            raise ValueError('Number must between 1 and 10')
        return v

class TtsRequest(BaseModel):
    message: str            # file path
    lang: str = TTS_LANG
    volume: int = 100

    @field_validator('volume')
    def validate_volume(cls, v):
        if v > 100 or v < 0:
            raise ValueError('Volume must between 0 and 100')
        return v

    @field_validator('lang')
    def validate_lang(cls, v):
        if v not in VOICES:
            #raise ValueError("Unknown voice, supported voices:{voices}".format(voices=VOICES))
            raise ValueError(f"Unknown voice, supported voices:{VOICES}")
        return v





@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    # Build a short, human-readable message
    errors = exc.errors()

    if errors:
        first = errors[0]
        loc = first.get("loc", [])
        msg = first.get("msg", "Invalid request")

        # Extract field name (e.g. body -> field)
        field = loc[-1] if len(loc) > 1 else "request"
        #message = f"{msg.capitalize()}: {field}"
        message = f"{msg}: {field}"
    else:
        message = "Invalid request"

    return JSONResponse(
        status_code=400,
        content={
            "error": "invalid_request",
            "message": message,
        },
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail.get("error", "unknown_error")
                     if isinstance(exc.detail, dict)
                     else "unknown_error",
            "message": exc.detail.get("message", str(exc.detail))
                     if isinstance(exc.detail, dict)
                     else str(exc.detail),
        },
    )


@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(favicon_path)



@app.post("/tts")
def tts_audio(req: TtsRequest):
    global player

    with player_lock:
        if player:
            player.stop()
            player.close()

        try:
            picotts = PicoTTS()
            #picotts.voice = "de-DE"
            #picotts.voice = TTS_LANG
            picotts.voice = req.lang
            wavs = picotts.synth_wav(req.message)

            player = AudioPlayer(
                source=wavs,
                loops=1,
                volume=req.volume/100
            )
            player.play()

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return {"status": "playing", "message": req.message, "lang": req.lang}


@app.post("/beep")
def beep_audio(req: BeepRequest):
    global player



    with player_lock:
        if player:
            player.stop()
            player.close()

        try:
            beepwav = BeepNoise()
            wav = beepwav.beep()

            signal, sr = beepnoise2.generate_sine_with_silence(
                frequency=880,
                tone_ms=250,
                silence_ms=250,
                samplerate=16000
            )

            player = AudioPlayer(
                source=signal,
                loops=req.number,
                volume=req.volume/100,
                samplerate=sr
            )
            player.play()

        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return {"status": "playing", "number": req.number}

@app.post("/play")
def play_audio(req: PlayRequest):
    global player

    with player_lock:
        if player:
            player.stop()
            player.close()

        try:
            path = os.path.join(AUDIO_DIR, req.filename)
            player = AudioPlayer(
                source=path,
                loops=1,
                volume=req.volume/100
            )
            player.play()
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return {"status": "playing", "filename": req.filename}


@app.post("/loop")
def loop_audio(req: LoopRequest):
    global player

    with player_lock:
        if player:
            player.stop()
            player.close()

        try:
            path = os.path.join(AUDIO_DIR, req.filename)
            #_LOGGER.info("path: %s" , path)
            player = AudioPlayer(
                source=path,
                loops=-1,
                volume=req.volume/100
            )
            #_LOGGER.info("path: %s" , path)
            player.play()
            #_LOGGER.info("path: %s" , path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    return {"status": "looping", "filename": req.filename, "max_duration_ms": 60000}


@app.get("/stop")
def stop_audio():
    global player

    with player_lock:
        if not player:
            return {"status": "idle"}

        player.stop()
        player.close()
        player = None

    return {"status": "stopped"}

@app.get("/status")
def status_audio():
    global player

    with player_lock:
        if not player:
            return {"status": "idle"}

    return {"status": "playing"}


@app.get("/info")
def info_audio():
    return {"info": {"name": "doorbell","host": "doorbell", "ip": "0.0.0.0", "port": 5000}}


if __name__ == "__main__":
    uvicorn.run("doorbell_api:app", host=HOST, port=PORT, reload=True, log_level=LOG_LEVEL.lower())
