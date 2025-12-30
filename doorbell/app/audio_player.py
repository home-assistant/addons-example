import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import time
import io

MAX_LOOP_MS = 60000


class AudioPlayer:
    def __init__(self, source, loops=1, volume=1.0):
        if isinstance(source, (bytes, bytearray)):
            source = io.BytesIO(source)

        # Decode ONCE
        self.data, self.samplerate = sf.read(source, dtype="float32")
        if self.data.ndim == 1:
            self.data = self.data[:, np.newaxis]

        self.channels = self.data.shape[1]
        self.total_frames = len(self.data)

        self.volume = float(volume)
        self.loops = loops

        self.position = 0
        self.current_loop = 0
        self.start_time = None

        self._stop_event = threading.Event()
        self._should_stop_after_block = False

        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype="float32",
            callback=self._callback,
            blocksize=2048,
            latency="high"
        )

    # --------------------------------------------------
    # PortAudio-safe callback (NO premature stop)
    # --------------------------------------------------
    def _callback(self, outdata, frames, time_info, status):
        outdata.fill(0)

        if self._stop_event.is_set():
            raise sd.CallbackStop()

        # Stop AFTER last buffer was fully sent
        if self._should_stop_after_block:
            raise sd.CallbackStop()

        # Hard loop time cap
        if self.start_time and (time.time() - self.start_time) * 1000 >= MAX_LOOP_MS:
            self._should_stop_after_block = True
            return

        filled = 0

        while filled < frames:
            remaining_data = self.total_frames - self.position
            remaining_out = frames - filled

            if remaining_data >= remaining_out:
                outdata[filled:filled + remaining_out] = \
                    self.data[self.position:self.position + remaining_out]
                self.position += remaining_out
                filled += remaining_out
            else:
                # End of audio
                outdata[filled:filled + remaining_data] = \
                    self.data[self.position:]
                filled += remaining_data

                self.current_loop += 1
                if self.loops == -1 or self.current_loop < self.loops:
                    self.position = 0
                else:
                    # IMPORTANT: do NOT stop yet
                    self._should_stop_after_block = True
                    break

        outdata *= self.volume

    # --------------------------------------------------
    # Controls
    # --------------------------------------------------
    def play(self):
        self.position = 0
        self.current_loop = 0
        self.start_time = time.time()
        self._should_stop_after_block = False
        self._stop_event.clear()
        self.stream.start()

    def stop(self):
        self._stop_event.set()
        if self.stream.active:
            self.stream.stop()

    def close(self):
        self.stop()
        self.stream.close()

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, float(volume)))
