FROM node:14.15-alpine

ARG N8N_VERSION=0.186.1

RUN if [ -z "$N8N_VERSION" ] ; then echo "The N8N_VERSION argument is missing!" ; exit 1; fi

# Update everything and install needed dependencies
RUN apk add --no-cache --update graphicsmagick tzdata git su-exec jq

# # Set a custom user to not have n8n run as root
USER root

#COPY warmup.sh /tmp/warmup.sh
#CMD ["sh", "/tmp/warmup.sh"]

# Install n8n and the also temporary all the packages
# it needs to build it correctly.
RUN apk --update add --virtual build-dependencies python build-base ca-certificates && \
    npm_config_user=root npm install -g full-icu sqlite3 n8n@${N8N_VERSION} && \
    apk del build-dependencies

# Install fonts
RUN apk --no-cache add --virtual fonts msttcorefonts-installer fontconfig && \
    update-ms-fonts && \
    fc-cache -f && \
    apk del fonts && \
    find  /usr/share/fonts/truetype/msttcorefonts/ -type l -exec unlink {} \;

ENV NODE_ICU_DATA /usr/local/lib/node_modules/full-icu

WORKDIR /data

COPY docker-entrypoint.sh /tmp/docker-entrypoint.sh
ENTRYPOINT ["sh", "/tmp/docker-entrypoint.sh"]

EXPOSE 5678/tcp


# Build arguments
ARG BUILD_ARCH
ARG BUILD_DATE
ARG BUILD_REF
ARG BUILD_VERSION
ARG IMAGE_SOURCE

# Labels
LABEL \
    io.hass.name="n8n" \
    io.hass.description="Automate without limits" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version=${BUILD_VERSION} \
    maintainer="L0rdShrek" \
    org.label-schema.description="Automate without limits" \
    org.label-schema.build-date=${BUILD_DATE} \
    org.label-schema.name="n8n" \
    org.label-schema.schema-version="1.0" \
    org.label-schema.url="https://addons.community" \
    org.label-schema.usage="https://github.com/hassio-addons/addon-example/tree/master/README.md" \
    org.label-schema.vcs-ref=${BUILD_REF} \
    org.label-schema.vcs-url="https://github.com/hassio-addons/addon-example" \
    org.label-schema.vendor="L0rdShrek"\
    org.opencontainers.image.source=${IMAGE_SOURCE}
