# This is to be run on the device, after the update
# This is only necessary is a registration (or re-registration) is needed

source /etc/register_config.sh

function REBOOT {
	echo "Do you want to reboot now?"
	select yn in "Yes" "No"; do
	    case $yn in
	        Yes ) reboot;;
	        No ) exit;;
	    esac
	done
}

function REGISTER {
  px-device-identity -o INIT \
		-s $DEVICE_SECURITY \
		-a $AUTH_SERVER_URL \
		-dn $AUTH_SERVER_DOMAIN \
		-r $DEVICE_ROLE \
		-t $DEVICE_NAME \
		-l $DEVICE_LOCATION \
		-f True
	exit
}

function EDIT_CONFIG {
  echo "Edit the configuration as desired with 'export AUTH_SERVER_URL=...'"
  echo "and then run 'sh /etc/register.sh' again"
	exit
}

function CONTINUE {
	echo "This is the configuration. Do you want to continue?"
	select yn in "Yes" "No"; do
	    case $yn in
	        Yes ) REGISTER;;
	        No ) EDIT_CONFIG;;
	    esac
	done
}

echo "### CONFIG"
echo ""
echo "AUTH_SERVER_URL: ${AUTH_SERVER_URL}"
echo "DEVICE_SECURITY: ${DEVICE_SECURITY}"
echo "AUTH_SERVER_DOMAIN: ${AUTH_SERVER_DOMAIN}"
echo "DEVICE_ROLE: ${DEVICE_ROLE}"
echo "DEVICE_NAME: ${DEVICE_NAME}"
echo "DEVICE_LOCATION: ${DEVICE_LOCATION}"
echo ""

CONTINUE

REBOOT