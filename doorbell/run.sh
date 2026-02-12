#!/usr/bin/with-contenv bashio
# shellcheck shell=bash

set -eo pipefail

echo "hello from doorbell!"

bashio::log.info "Starting Example Config Copier add-on"


SRC_DIR="/app/homeassistant/doorbell"
DST_DIR="/homeassistant/custom_components/doorbell"

# Safety checks
if [ ! -d "${SRC_DIR}" ]; then
  bashio::log.error "Source directory ${SRC_DIR} not found"
  exit 1
fi

if [ ! -d "${DST_DIR}" ]; then
  bashio::log.info "Destination ${DST_DIR} does not exist, creating..."
  mkdir -p "${DST_DIR}"
fi

bashio::log.info "Copying files from ${SRC_DIR} to ${DST_DIR} (overwriting existing files)"
# Use rsync to mirror the data directory into /config, overwrite by default
rsync -a -vv --delete --no-perms --no-owner --no-group "${SRC_DIR}/" "${DST_DIR}/"

# Optionally set a marker file with timestamp to indicate last copy
date -u +"%Y-%m-%dT%H:%M:%SZ" > "${DST_DIR}/.addon_config_copied_timestamp"

bashio::log.info "Config copy completed"


#**Why `rsync`?**
#- `rsync -a` preserves directory structure and copies recursively.
#- `--ignore-existing` used in preserve mode prevents overwriting user files.
#- `--delete` in overwrite mode keeps destination mirrored to the source (be careful: this removes files in /config that are *not* present in /data).
# If you do not want deletion behavior, remove `--delete`.





bashio::log.info "doing discovery ..."


bashio::log.info "$(bashio::addon.hostname)"
bashio::log.info "$(bashio::addon.port 5000)"
bashio::log.info "$(bashio::config 'port')"


#bashio::discovery "doorbell" "${config}" > /dev/null
#bashio::log.info "Published discovery: host=my_example_addon port=${PORT}"

bashio::log.info "setting env variables ..."


CONF_HOST=$(bashio::config 'host')
#CONF_PORT=$(bashio::addon.port 5000)
LOG_LEVEL=$(bashio::config 'log_level')
TTS_LANG=$(bashio::config 'tts_lang')
DOORBELL_OUTPUT=$(bashio::config 'output')

#bashio::log.info "Starting API on ${CONF_HOST}:${CONF_PORT}"

export API_HOST="${CONF_HOST}"
#export API_PORT="${CONF_PORT}"
export LOG_LEVEL="${LOG_LEVEL}"
export TTS_LANG="${TTS_LANG}"
export DOORBELL_OUTPUT="${DOORBELL_OUTPUT}"

bashio::log.info "possible outputs ..."

exec python3 -m sounddevices

bashio::log.info "starting up ..."
#exec /usr/local/bin/doorbell-discovery.sh



#exec python3 /app/run.py
exec python3 /app/doorbell_api.py
#exec uvicorn doorbell_api:app --host 0.0.0.0 --port "$API_PORT"

