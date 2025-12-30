import numpy as np

# Parameters
samplerate = 48000   # Hz
frequency = 880      # Hz
tone_duration = 0.25 # seconds
silence_duration = 0.25


class BeepNoise2(object):

    def __init__(self, freq :int=880, duration :int=250, samplerate: int=16000 ):
        self._freq = freq
        self._duration = duration/1000
        self._sample_rate = samplerate
        #self._sample_rate = 48000
        #self._volume = 1.0
        #self._audio = []

    def beep(self):
        # Time axes
        t_tone = np.linspace(0, self._duration, int(self._sample_rate * self._duration), False)
        t_silence = np.zeros(int(self._sample_rate * self._duration))

        # Generate sine wave
        tone = 0.5 * np.sin(2 * np.pi * self._freq * t_tone)

        # Concatenate tone + silence
        signal = np.concatenate([tone, t_silence])

        return signal


def generate_sine_with_silence(
    frequency=880,
    tone_ms=250,
    silence_ms=250,
    samplerate=16000,
    amplitude=1,
    channels=1
):
    tone_samples = int(samplerate * tone_ms / 1000)
    silence_samples = int(samplerate * silence_ms / 1000)

    t = np.arange(tone_samples) / samplerate
    tone = amplitude * np.sin(2 * np.pi * frequency * t)

    silence = np.zeros(silence_samples, dtype=np.float32)

    signal = np.concatenate([tone, silence]).astype(np.float32)

    # Mono → stereo if needed
    if channels > 1:
        signal = np.repeat(signal[:, np.newaxis], channels, axis=1)
    else:
        signal = signal[:, np.newaxis]

    return signal, samplerate
