import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time
import io

MAX_LOOP_MS = 60000


class AudioPlayer:
    def __init__(self, source, loops=1, volume=1.0):
        """
        source : file path | bytes | BytesIO
        loops  : number of repeats, -1 = infinite (capped at 60s)
        volume : 0.0 .. 1.0
        """

        # ---- Load audio ONCE (no decoding in callback) ----
        if isinstance(source, (bytes, bytearray)):
            source = io.BytesIO(source)

        self.data, self.samplerate = sf.read(source, dtype="float32")

        # Normalize mono → (N, 1)
        if self.data.ndim == 1:
            self.data = self.data[:, np.newaxis]

        self.channels = self.data.shape[1]
        self.total_frames = len(self.data)

        # ---- Playback state ----
        self.volume = float(volume)
        self.loops = loops
        self.current_loop = 0
        self.position = 0
        self.start_time = None

        self._stop_event = threading.Event()
        self._lock = threading.Lock()

        # ---- Audio stream (stable config) ----
        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
            blocksize=2048,
            latency="high"
        )

    # ---------------------------------------------------
    # Real-time safe callback (NO allocations / IO)
    # ---------------------------------------------------
    def _callback(self, outdata, frames, time_info, status):
        if self._stop_event.is_set():
            outdata.fill(0)
            raise sd.CallbackStop()

        # Hard loop duration cap
        if self.start_time and (time.time() - self.start_time) * 1000 >= MAX_LOOP_MS:
            raise sd.CallbackStop()

        filled = 0

        while filled < frames:
            remaining_data = self.total_frames - self.position
            remaining_out = frames - filled

            if remaining_data >= remaining_out:
                # Normal case
                outdata[filled:filled + remaining_out] = \
                    self.data[self.position:self.position + remaining_out]
                self.position += remaining_out
                filled += remaining_out
            else:
                # End of buffer reached
                outdata[filled:filled + remaining_data] = \
                    self.data[self.position:self.total_frames]
                filled += remaining_data

                self.current_loop += 1
                if self.loops == -1 or self.current_loop < self.loops:
                    self.position = 0
                else:
                    # No more loops → stop exactly here
                    outdata[filled:] = 0
                    raise sd.CallbackStop()

        outdata *= self.volume


    # ---------------------------------------------------
    # Controls
    # ---------------------------------------------------
    def play(self):
        self._stop_event.clear()
        self.position = 0
        self.current_loop = 0
        self.start_time = time.time()
        self.stream.start()

    def stop(self):
        self._stop_event.set()
        if self.stream.active:
            self.stream.stop()

    def close(self):
        self.stop()
        self.stream.close()

    # ---------------------------------------------------
    # Volume
    # ---------------------------------------------------
    def set_volume(self, volume):
        with self._lock:
            self.volume = max(0.0, min(1.0, float(volume)))

    def fade_to(self, target, duration_ms=500):
        steps = 50
        step_time = duration_ms / steps / 1000
        delta = (target - self.volume) / steps

        def _fade():
            for _ in range(steps):
                with self._lock:
                    self.volume += delta
                time.sleep(step_time)

        threading.Thread(target=_fade, daemon=True).start()
