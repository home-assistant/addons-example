#!/bin/bash
sed -e

CONFIG_PATH=/data/options.json

TARGET=$(jq --raw-output ".target" $CONFIG_PATH)
USERNAME=$(jq --raw-output ".username" $CONFIG_PATH)
PASSWORD=$(jq --raw-output ".password" $CONFIG_PATH)

echo "fake copy from /config to $TARGET@$USERNAME"
