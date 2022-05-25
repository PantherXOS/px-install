#!/bin/bash
# Version 0.0.2

echo "Make sure to run this from within ./scripts directory!"

read -p "Device Model (Thinkstation 625, Onlogic, Calmo) [Onlogic]: " DEVICE_MODEL
DEVICE_MODEL=${DEVICE_MODEL:-'Onlogic'}
echo $DEVICE_MODEL

read -p "Channels file (full path) [./resources/channels.scm]: " CHANNELS_FILE 
CHANNELS_FILE=${CHANNELS_FILE:-'./resources/channels.scm'}
echo $CHANNELS_FILE

read -p "System config file (full path) [./resources/system.scm]: " CONFIG_FILE 
CONFIG_FILE=${CONFIG_FILE:-'./resources/system.scm'}
echo $CONFIG_FILE

## Registration specific

read -p "Auth server URL [https://identity.pantherx.org]: " AUTH_SERVER_URL 
AUTH_SERVER_URL=${AUTH_SERVER_URL:-'https://identity.pantherx.org'}
echo $AUTH_SERVER_URL

read -p "Device security (STANDARD|TPM) [STANDARD]: " DEVICE_SECURITY 
DEVICE_SECURITY=${DEVICE_SECURITY:-'STANDARD'}
echo $DEVICE_SECURITY

read -p "Auth server domain [pantherx.org]: " AUTH_SERVER_DOMAIN 
AUTH_SERVER_DOMAIN=${AUTH_SERVER_DOMAIN:-'pantherx.org'}
echo $AUTH_SERVER_DOMAIN

read -p "Device role (PUBLIC|DESKTOP|SERVER|ADMIN_TERMINAL|REGISTRATION_TERMINAL|OTHER|SELF) [DESKTOP]: " DEVICE_ROLE 
DEVICE_ROLE=${DEVICE_ROLE:-'DESTKOP'}
echo $DEVICE_ROLE

echo "IMPORTANT: Do not use special characters like #; If you use more than one word, do: 'two words'."
read -p "Device name [PantherX Desktop]: " DEVICE_NAME 
DEVICE_NAME=${DEVICE_NAME:-'PantherX Desktop'}
echo $DEVICE_NAME

read -p "Device location [Office]: " DEVICE_LOCATION 
DEVICE_LOCATION=${DEVICE_LOCATION:-'Office'}
echo $DEVICE_LOCATION

read -p "Time zone [Europe/Berlin]: " TIME_ZONE 
TIME_ZONE=${TIME_ZONE:-'Europe/Berlin'}
echo $TIME_ZONE

scripts_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source ${scripts_dir}/_pack-config.sh