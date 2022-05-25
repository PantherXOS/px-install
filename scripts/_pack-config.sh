#!/bin/bash
# IMPORTANT
# Do not call this directly; use pack-config.sh instead: ./pack-config.sh

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
cp $CONFIG_FILE "${TEMP}/system.scm"
##
# cp ../configuration/system.scm $TEMP

cat >$TEMP/config.json <<EOL
{
	"type":"${DEVICE_ROLE}",
	"timezone":"${TIME_ZONE}",
	"locale":"en_US.utf8",
	"title":"${DEVICE_NAME}",
	"location":"${DEVICE_LOCATION}",
	"role":"${DEVICE_ROLE}",
	"key_security":"${DEVICE_SECURITY}",
	"key_type":"RSA:2048",
	"domain":"${AUTH_SERVER_DOMAIN}",
	"host":"${AUTH_SERVER_URL}"
}
EOL

tar -cvzf ${PACK_SETUP_FILE_NAME} -C $TEMP .

DATE=$(date)
GOOD_CONFIG="${DATE}, ${DEVICE_MODEL}, ${DEVICE_ROLE}, ${AUTH_SERVER_URL}, ${PACK_SETUP_FILE_ID} (${TIME_ZONE})"
echo $GOOD_CONFIG >> last_good_config.txt

echo "########"
echo ""
echo "Provide the commands to the user:"
echo "1. Run setup with: px-install --config ${PACK_SETUP_FILE_ID}"
echo ""
echo "########"

trap '{ rm -rf -- "$PACK_CONFIG_TEMP_DIR"; }' EXIT

echo "S3 Upload: AWS access and secret keys need to be set in advance!"
read -p "Would you like to upload the config to S3? [yes]: " USER_RESPONSE_UPLOAD_S3 
USER_RESPONSE_UPLOAD_S3=${USER_RESPONSE_UPLOAD_S3:-'yes'}
echo $AUTH_SERVER_URL

if [ $USER_RESPONSE_UPLOAD_S3 = 'yes' ]; then
	echo "=> Uploading to S3"
s3cmd put \
--access_key=$AWS_ACCESS_KEY \
--secret_key=$AWS_SECRET_KEY \
--region=eu-central-1 \
--acl-public \
$PACK_SETUP_FILE_NAME \
$AWS_BUCKET_URL
fi