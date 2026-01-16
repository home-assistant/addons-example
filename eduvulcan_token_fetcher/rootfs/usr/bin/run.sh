#!/usr/bin/with-contenv bashio
# ==============================================================================
# EduVulcan Token Fetcher
# ==============================================================================

declare login
declare password

login=$(bashio::config 'login')
password=$(bashio::config 'password')

if bashio::var.is_empty "${login}"; then
  bashio::log.fatal "Missing required config: login"
  exit 1
fi

if bashio::var.is_empty "${password}"; then
  bashio::log.fatal "Missing required config: password"
  exit 1
fi

export EDUVULCAN_LOGIN="${login}"
export EDUVULCAN_PASSWORD="${password}"

bashio::log.info "Starting EduVulcan token fetcher"

exec python3 /app/main.py
