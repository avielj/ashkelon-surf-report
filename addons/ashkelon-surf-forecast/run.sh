#!/bin/bash

echo "Starting Ashkelon Surf Forecast Home Assistant Addon..."

# Get configuration from Home Assistant
CONFIG_PATH="/data/options.json"
UPDATE_INTERVAL=$(jq --raw-output '.update_interval' $CONFIG_PATH)
TIMEZONE=$(jq --raw-output '.timezone' $CONFIG_PATH)
SHOW_HEBREW=$(jq --raw-output '.show_hebrew' $CONFIG_PATH)
SHOW_CHART=$(jq --raw-output '.show_chart' $CONFIG_PATH)

echo "Configuration:"
echo "  Update Interval: ${UPDATE_INTERVAL} seconds"
echo "  Timezone: ${TIMEZONE}"
echo "  Show Hebrew: ${SHOW_HEBREW}"
echo "  Show Chart: ${SHOW_CHART}"

# Set timezone
export TZ=${TIMEZONE}

# Export configuration as environment variables
export UPDATE_INTERVAL
export SHOW_HEBREW
export SHOW_CHART

# Start the web server
echo "Starting web server on port 8099..."
python web_server.py
