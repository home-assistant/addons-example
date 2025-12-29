import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import io
import time
import logging

MAX_LOOP_MS = 60000  # 60 seconds

_LOGGER = logging.getLogger(__name__)

class AudioPlayer:
    def __init__(self, source, loops=1, volume=1.0):
        """
        source : filename (str) OR BytesIO OR bytes
        loops  : number of repeats, -1 = infinite (but capped at 60s)
        volume : 0.0 .. 1.0
        """

        self.volume = float(volume)
        self.loops = loops
        self.start_time = None

        #_LOGGER.info("loops %s", self.loops)

        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # ---- Open source ----
        if isinstance(source, (bytes, bytearray)):
            #print("ist bytes")
            source = io.BytesIO(source)

        self.file = sf.SoundFile(source)
        self.samplerate = self.file.samplerate
        self.channels = self.file.channels
        #print(f"sample rate: {self.samplerate}")
        #print(f"channels : {self.channels}")

        self.current_loop = 0

        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback
        )

    # ---------- Audio callback ----------
    def _callback(self, outdata, frames, time_info, status):
        if self._stop_event.is_set():
            outdata.fill(0)
            raise sd.CallbackStop()

        # Enforce max loop duration
        if self.start_time and (time.time() - self.start_time) * 1000 >= MAX_LOOP_MS:
            raise sd.CallbackStop()

        #print(f"frames: {frames}")

        data = self.file.read(frames, dtype="float32")
        #print(f"len data: {len(data)}")

        if data.ndim == 1:
            data = data[:, np.newaxis]

        if len(data) < frames:
            #print("X")
            outdata[:len(data)] = data
            outdata[len(data):] = 0

            self.current_loop += 1
            if self.loops == -1 or self.current_loop < self.loops:
                self.file.seek(0)
            else:
                raise sd.CallbackStop()
        else:
            #None
            #print(f"else: {len(data)}")
            outdata[:] = data
            #outdata[:] = data

        # Apply volume (thread-safe)
        with self._lock:
            outdata *= self.volume

    # ---------- Controls ----------
    def play(self):
        self._stop_event.clear()
        self.file.seek(0)
        self.current_loop = 0
        self.start_time = time.time()
        self.stream.start()

    def stop(self):
        self._stop_event.set()
        self.stream.stop()
        self.file.seek(0)
        self.current_loop = 0

    def close(self):
        self.stop()
        self.stream.close()
        self.file.close()

    # ---------- Volume ----------
    def set_volume(self, volume):
        """Set volume: 0.0 .. 1.0"""
        with self._lock:
            self.volume = max(0.0, min(1.0, float(volume)))

    def fade_to(self, target, duration_ms=500):
        """Smooth volume fade"""
        steps = 50
        step_time = duration_ms / steps / 1000
        delta = (target - self.volume) / steps

        def _fade():
            for _ in range(steps):
                with self._lock:
                    self.volume += delta
                time.sleep(step_time)

        threading.Thread(target=_fade, daemon=True).start()

'''
print("Play MP3 file (background)")

player = AudioPlayer("../audio-files/ding_dong.mp3", loops=3, volume=0.7)
player.play()
time.sleep(2)
player.stop()
time.sleep(1)

print("Infinite loop (auto-stops at 60s)")

player = AudioPlayer("../audio-files/ding_dong.mp3", loops=-1)
player.play()

time.sleep(2)

print("Change volume while playing")

player.set_volume(0.3)

time.sleep(2)

player.fade_to(1.0, duration_ms=1000)

time.sleep(2)

player.stop()
time.sleep(1)

print("Play from BytesIO / memory")

with open("../audio-files/ding_dong.mp3", "rb") as f:
    data = f.read()

player = AudioPlayer(data, loops=2, volume=0.8)
player.play()

time.sleep(2)

player.stop()
player.close()
'''
