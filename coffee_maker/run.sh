#!/bin/bash
sed -e

CONFIG_PATH=/data/options.json

DEVICE=$(jq --raw-output ".device" $CONFIG_PATH)

echo "We can now make coffee on device: $DEVICE"
