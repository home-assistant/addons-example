ARG BUILD_FROM=ghcr.io/hassio-addons/base-python:latest
FROM $BUILD_FROM

ENV LANG=C.UTF-8

# Setup base, install pulseaudio & sox package
RUN apk update
RUN echo #############################################
RUN apk search pip
RUN echo #############################################
RUN apk add --no-cache \
    rsync \
    gcc \
    g++ \
    jq \
    pulseaudio \
    pulseaudio-utils \
    alsa-plugins-pulse \
    picotts \
    sox \
    alsa-lib-dev \
    ffmpeg \
    python3 \
    python3-dev \
    py3-pip \
    py3-pyaudio

RUN pip3 install --no-cache-dir -U \
    setuptools \
    wheel

WORKDIR /app

COPY /app/requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

COPY /app/run.py /app/run.py
RUN chmod +x /app/run.py

COPY /app/audio.py /app/audio.py
RUN chmod +x /app/audio.py
COPY /app/beepnoise.py /app/beepnoise.py
RUN chmod +x /app/beepnoise.py
COPY /app/const.py /app/const.py
RUN chmod +x /app/const.py
COPY /app/controller.py /app/controller.py
RUN chmod +x /app/controller.py
COPY /app/pico2wave.py /app/pico2wave.py
RUN chmod +x /app/pico2wave.py

COPY /app/doorbell_api.py /app/doorbell_api.py
COPY /app/audio_player.py /app/audio_player.py
COPY /app/beepnoise2.py /app/beepnoise2.py

COPY /app/favicon.ico /app/favicon.ico

RUN chmod +x /app/doorbell_api.py
RUN chmod +x /app/audio_player.py
RUN chmod +x /app/beepnoise2.py


COPY run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

COPY doorbell-discovery.sh /usr/local/bin/doorbell-discovery.sh
RUN chmod +x /usr/local/bin/doorbell-discovery.sh

COPY install.sh /usr/local/bin/install.sh
# Ensure scripts are executable
RUN chmod +x /usr/local/bin/install.sh

#COPY audio.py /usr/local/bin/audio.py
#COPY config.py /usr/local/bin/config.py
#COPY controller.py /usr/local/bin/controller.py
#COPY pico2wave.py /usr/local/bin/pico2wave.py
#COPY beepnoise.py /usr/local/bin/beepnoise.py


COPY audio-files/ /app/audio-files/

COPY custom_components/ /app/homeassistant/


#CMD [ "python3", "/usr/local/bin/run.py" ]

CMD [ "/usr/local/bin/run.sh" ]
