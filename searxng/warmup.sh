#!/bin/sh
CONFIG_PATH="/data/options.json"


export VUE_APP_URL_BASE_API="$(jq --raw-output '.webhook_url // empty' $CONFIG_PATH)"