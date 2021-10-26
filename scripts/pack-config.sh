echo "Make sure to run this from within ./scripts directory!"


read -p "Channels file (full path) [./ressources/channels.scm]: " CHANNELS_FILE 
CHANNELS_FILE=${CHANNELS_FILE:-'./ressources/channels.scm'}
echo $CHANNELS_FILE

read -p "System config file (full path) [./ressources/system.scm]: " CONFIG_FILE 
CONFIG_FILE=${CONFIG_FILE:-'./ressources/system.scm'}
echo $CONFIG_FILE

## Registration specific

read -p "Auth server URL [https://identity.pantherx.org]: " AUTH_SERVER_URL 
AUTH_SERVER_URL=${AUTH_SERVER_URL:-'https://identity.pantherx.org'}
echo $AUTH_SERVER_URL

read -p "Device security [STANDARD]: " DEVICE_SECURITY 
DEVICE_SECURITY=${DEVICE_SECURITY:-'STANDARD'}
echo $DEVICE_SECURITY

read -p "Auth server domain [pantherx.org]: " AUTH_SERVER_DOMAIN 
AUTH_SERVER_DOMAIN=${AUTH_SERVER_DOMAIN:-'pantherx.org'}
echo $AUTH_SERVER_DOMAIN

read -p "Device role (PUBLIC|DESKTOP|SERVER|ADMIN_TERMINAL|REGISTRATION_TERMINAL|SELF) [DESKTOP]: " DEVICE_ROLE 
DEVICE_ROLE=${DEVICE_ROLE:-'DESTKOP'}
echo $DEVICE_ROLE

read -p "Device name [PantherX Desktop]: " DEVICE_NAME 
DEVICE_NAME=${DEVICE_NAME:-'PantherX Desktop'}
echo $DEVICE_NAME

read -p "Device location [Office]: " DEVICE_LOCATION 
DEVICE_LOCATION=${DEVICE_LOCATION:-'Office'}
echo $DEVICE_LOCATION

PACK_SETUP_FILE_ID=$(cat /dev/urandom | tr -cd 'a-f0-9' | head -c 10)
PACK_SETUP_FILE_NAME="${PACK_SETUP_FILE_ID}.tar.gz"

TEMP=$(mktemp -d -t ci-XXXXXXXXX)
export PACK_CONFIG_TEMP_DIR=${TEMP}

source ./config.sh

echo "### CONFIG"
echo ""
echo "AUTH_SERVER_URL: ${AUTH_SERVER_URL}"
echo "DEVICE_SECURITY: ${DEVICE_SECURITY}"
echo "AUTH_SERVER_DOMAIN: ${AUTH_SERVER_DOMAIN}"
echo "DEVICE_ROLE: ${DEVICE_ROLE}"
echo "DEVICE_NAME: ${DEVICE_NAME}"
echo "DEVICE_LOCATION: ${DEVICE_LOCATION}"
echo ""

echo "Packing config ${PACK_SETUP_FILE_ID} to ${PACK_SETUP_FILE_NAME}"

echo "Channels file: ${CHANNELS_FILE}"

cp $CHANNELS_FILE "${TEMP}/channels.scm"
## ADJUST SYSTEM HERE
cp $CONFIG_FILE "${TEMP}/config.scm"
##
# cp ../configuration/system.scm $TEMP

cat >$TEMP/config.json <<EOL
{
	"type":"ENTERPRISE",
	"timezone":"Europe/Berlin",
	"locale":"en_US.utf8",
	"title":"${DEVICE_NAME}",
	"location":"${DEVICE_LOCATION}",
	"role":"${DEVICE_ROLE}",
	"key_security":"${DEVICE_SECURITY}",
	"domain":"${AUTH_SERVER_DOMAIN}",
	"host":"${AUTH_SERVER_URL}"
}
EOL

cp './ressources/register.sh' $TEMP

tar -cvzf ${PACK_SETUP_FILE_NAME} -C $TEMP .

echo "########"
echo ""
echo "Provide the commands to the user:"
echo "1. Run setup with: px-install --config ${PACK_SETUP_FILE_ID}"
echo ""
echo "########"

trap '{ rm -rf -- "$PACK_CONFIG_TEMP_DIR"; }' EXIT