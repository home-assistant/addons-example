# https://developers.home-assistant.io/docs/add-ons/configuration#add-on-dockerfile
ARG ghcr.io/kiwix/kiwix-tools:3.1.2
FROM $BUILD_FROM

# Execute during the build of the image
ARG TEMPIO_VERSION BUILD_ARCH
RUN \
    curl -sSLf -o /usr/bin/tempio \
    "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_${BUILD_ARCH}"

# Copy root filesystem
COPY rootfs /
RUN apk add --no-cache cron
RUN echo "0 2 * * * /usr/bin/run_kiwix --update" > /etc/crontabs/root
