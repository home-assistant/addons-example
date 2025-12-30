import math
import wave
import struct
import tempfile


# Audio will contain a long list of samples (i.e. floating point numbers describing the
# waveform).  If you were working with a very long sound you'd want to stream this to
# disk instead of buffering it all in memory list this.  But most sounds will fit in
# memory.
#audio = []
#sample_rate = 44100.0

class BeepNoise(object):

    def __init__(self, freq :int=880, duration :int=250 ):
        self._freq = freq
        self._duration = duration
        self._sample_rate = 22050
        self._volume = 1.0
        self._audio = []

    def beep(self):

        self._append_sinewave(self._freq, self._duration, self._volume)
        self._append_silence(self._duration)

        tmp_file_name = tempfile.TemporaryFile(dir=".",suffix=".wav")

        wav_file=wave.open(tmp_file_name,"w")

        # wav params
        nchannels = 1
        sampwidth = 2

        # 44100 is the industry standard sample rate - CD quality. If you need to
        # save on file size you can adjust it downwards. The stanard for low quality
        # is 8000 or 8kHz.
        nframes = len(self._audio)
        comptype = "NONE"
        compname = "not compressed"
        wav_file.setparams((nchannels, sampwidth, self._sample_rate, nframes, comptype, compname))

        # WAV files here are using short, 16 bit, signed integers for the
        # sample size.  So we multiply the floating point data we have by 32767, the
        # maximum value for a short integer.  NOTE: It is theortically possible to
        # use the floating point -1.0 to 1.0 data directly in a WAV file but not
        # obvious how to do that using the wave module in python.
        for sample in self._audio:
            wav_file.writeframes(struct.pack('h', int( sample * 32767.0 )))

        wav_file.close()

        wav = None

        with tmp_file_name as f:
            f.seek(0)
            wav = f.read()

        return wav



    def _append_silence(self, duration_milliseconds):
        """
        Adding silence is easy - we add zeros to the end of our array
        """
        num_samples = duration_milliseconds * (self._sample_rate / 1000.0)

        for x in range(int(num_samples)):
            self._audio.append(0.0)

        return


    def _append_sinewave(self,
            freq=880.0,
            duration_milliseconds=250,
            volume=1.0):
        """
        The sine wave generated here is the standard beep.  If you want something
        more aggresive you could try a square or saw tooth waveform.   Though there
        are some rather complicated issues with making high quality square and
        sawtooth waves... which we won't address here :)
        """

        #global audio # using global variables isn't cool.

        num_samples = duration_milliseconds * (self._sample_rate / 1000.0)

        for x in range(int(num_samples)):
            self._audio.append(volume * math.sin(2 * math.pi * freq * ( x / self._sample_rate )))

        return


    def save_wav(self, file_name):
        # Open up a wav file
        wav_file=wave.open(file_name,"w")

        # wav params
        nchannels = 1

        sampwidth = 2

        # 44100 is the industry standard sample rate - CD quality. If you need to
        # save on file size you can adjust it downwards. The stanard for low quality
        # is 8000 or 8kHz.
        nframes = len(self._audio)
        comptype = "NONE"
        compname = "not compressed"
        wav_file.setparams((nchannels, sampwidth, self._sample_rate, nframes, comptype, compname))

        # WAV files here are using short, 16 bit, signed integers for the
        # sample size.  So we multiply the floating point data we have by 32767, the
        # maximum value for a short integer.  NOTE: It is theortically possible to
        # use the floating point -1.0 to 1.0 data directly in a WAV file but not
        # obvious how to do that using the wave module in python.
        for sample in self._audio:
            wav_file.writeframes(struct.pack('h', int( sample * 32767.0 )))

        wav_file.close()

        return

#append_sinewave(volume=0.25)
#append_silence()
#append_sinewave(volume=0.5)
#append_silence()
#append_sinewave()
#save_wav("output.wav")

#beepwav = BeepNoise()
#wav = beepwav.beep()
#beepwav.save_wav("test.wav")
