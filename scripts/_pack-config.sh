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

## UPLOAD

echo "=> Uploading new archive to S3"
INI_FILE=~/.aws/credentials

while IFS=' = ' read key value
do
    if [[ $key == \[*] ]]; then
        section=$key
    elif [[ $value ]] && [[ $section == '[temp-pantherx]' ]]; then
        if [[ $key == 'aws_access_key_id' ]]; then
            AWS_ACCESS_KEY_ID=$value
        elif [[ $key == 'aws_secret_access_key' ]]; then
            AWS_SECRET_ACCESS_KEY=$value
        fi
    fi
done < $INI_FILE

echo "AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID"
echo "AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY"

##

if [[ -z "$AWS_ACCESS_KEY_ID" ]]; then
    echo "AWS_ACCESS_KEY_ID is empty"
    echo "Please check your ~/.aws/credentials file"
fi

s3cmd put \
--access_key=$AWS_ACCESS_KEY_ID \
--secret_key=$AWS_SECRET_ACCESS_KEY \
--region=eu-central-1 \
--acl-public \
$PACK_SETUP_FILE_NAME \
$AWS_BUCKET_URL