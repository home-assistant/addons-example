# Home Assistant Add-on: Doobell add-on

_Doorbell add-on for playing audio files on local audio cards._

Provides a Rest API on port 5000

endpoints:

```
/play
    play audio files
/loop
    loop audio files
/tts
    text-to-speex with pico tts
/beep
    doing beepnoise
/stop
    stop playing
/status
    status of doorbell (playing/idle)
```

presets audio files:

```
alarm.mp3
ba_dum_tss.mp3
bells_2.mp3
bells.mp3
bright.mp3
chirp.mp3
choir.mp3
chord.mp3
classical.mp3
crickets.mp3
ding_dong.mp3
ding.mp3
doorbell.mp3
drumroll.mp3
dun_dun_dun.mp3
error.mp3
fanfare.mp3
glockenspiel.mp3
hail.mp3
knock.mp3
marimba.mp3
mario_coin.mp3
microphone_tap.mp3
sad_trombone.mp3
soft.mp3
tada.mp3
toast.mp3
twenty_four.mp3
westminster.mp3
whistle.mp3
```

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
