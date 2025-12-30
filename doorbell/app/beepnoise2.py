import numpy as np


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
