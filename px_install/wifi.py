import json
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Union

from px_install.util import print_debug_qr_code, run_commands


@dataclass
class AddressInfo():
	family: str
	local: str
	broadcast: Union[str, None]


@dataclass
class NetworkInterface():
	name: str
	operstate: str
	addr_info: List[AddressInfo]


def get_wifi_interface_names():
	'''
	List all Wi-Fi adapter adapter on the system
	'''
	result_list = []
	try:
		process = subprocess.run(['ls /sys/class/ieee80211/*/device/net/'], capture_output=True, text=True, shell=True, check=True)
		result = process.stdout
		result_list = result.split(" ")
	except:
		print('Could not determine available Wi-Fi adapter.')

	valid_names = []

	if len(result_list) > 0:
		for name in result_list:
			data = name.replace("\n", "")
			valid_names.append(data)

	return valid_names


def list_network_interfaces(filter_param: Union[str, None] = None):
	'''
	List all network interfaces on the system

	Use the filter:
	- for Wi-Fi: 'wifi'
	'''
	default_filter = ['lo']

	process = subprocess.run(['ip', '--json', 'a'], capture_output=True, text=True, check=True)
	result = json.loads(process.stdout)

	valid_interfaces = []
	for interface in result:

		addr_info = []
		if 'addr_info' in interface and len(interface['addr_info']) > 0:
			for info in interface['addr_info']:
				broadcast = None
				if 'broadcast' in info:
					broadcast = info['broadcast']
				addr_info.append(AddressInfo(
					family=info['family'],
					local=info['local'],
					broadcast=broadcast
				))

		formatted_interface = NetworkInterface(
				name=interface['ifname'],
				operstate=interface['operstate'],
				addr_info=addr_info
			)
		ifname = interface['ifname']
		if filter_param is not None:
			if filter_param == 'wifi':
				valid_names = get_wifi_interface_names()
				if ifname in valid_names:
					valid_interfaces.append(formatted_interface)
				else:
					print('Interface {} did not pass the filter: {}.'.format(formatted_interface.name, filter_param))
			else:
				print('Invalid filter: {}'.format(filter_param))
		else:
			if ifname not in default_filter:
				valid_interfaces.append(formatted_interface)

	# for item in valid_interfaces:
	#     print(item)

	return valid_interfaces


def prompt_for_wifi_config():
	'''
	Prompt for common Wi-Fi settings
	'''
	print()
	ssid = input("Enter your wireless name: ")
	print('-> Selected: {}'.format(ssid))
	print('')
	print('Network security:')
	print("- 'NONE' (open network)")
	print("- 'WEP' (broken, insecure)")
	print("- 'WPA-PSK' (WPA-Personal)")
	key_mgmt = input("Specify your network security. ['WPA-PSK']: ") or 'WPA-PSK'
	print('-> Selected: {}'.format(key_mgmt))
	print()
	psk = input("Enter your WiFi password: ")
	print('-> Entered: {}'.format(psk))
	print()
	print('######## SUMMARY ########')
	print()
	print("Name: {}".format(ssid))
	print("Security: {}".format(key_mgmt))
	print("Password: {}".format(psk))
	print()
	approved = input("Approve WiFi config with 'yes'; cancel with 'no': ")
	if approved.lower() != 'yes':
		print('You did not approve. Exiting...')
		sys.exit()
	return {
		'ssid': ssid,
		'key_mgmt': key_mgmt,
		'psk': psk
	}


def write_wifi_config(config, file_path='/root/wpa_supplicant.conf'):
	if config['key_mgmt'] == 'WEP':
		content = '''network={{
	ssid="{}"
	key_mgmt=NONE
	wep_key0="{}"
	wep_tx_keyidx=0
}}'''.format(config['ssid'], config['psk'])
	else:
		content = '''network={{
	ssid="{}"
	key_mgmt={}
	psk="{}"
}}'''.format(config['ssid'], config['key_mgmt'], config['psk'])
	with open(file_path, 'w') as writer:
		writer.write(content)


# def install_wpa_supplicant():
# 	commands = [['guix', 'package', '-i', 'wpa_supplicant']]
# 	run_commands(commands)


def rfkill_unblock_wifi():
	commands = [['rfkill', 'unblock', 'wifi']]
	run_commands(commands)
	

def wpa_supplicant_activate():
	wifi_networks = list_network_interfaces('wifi')
	if len(wifi_networks) > 0:
		network = wifi_networks[0]
		commands = [['wpa_supplicant', '-c', '/root/wpa_supplicant.conf', '-i', network.name, '-B']]
		run_commands(commands)


def dhclient_get_ip():
	wifi_networks = list_network_interfaces('wifi')
	if len(wifi_networks) > 0:
		network = wifi_networks[0]
		commands = [['dhclient', '-v', network.name]]
		run_commands(commands)


def has_valid_wifi_interface():
	'''
	Check if a valid Wi-Fi adapter was found on the system
	'''
	wifi_networks = list_network_interfaces('wifi')

	if len(wifi_networks) > 0:
		return True
	else:
		print()
		print('######## ERROR ########')
		print()
		print('Could not detect a Wi-Fi interface on your computer.')
		print('(1) On some devices you need to unblock the inteface with: rfkill unblock wifi')
		print('(2) Your Wi-Fi interface is not supported out of the box')
		print('=> If anyhow possible, install with a LAN cable.')
		print()
		print('Consult https://wiki.pantherx.org/Installation-guide/#connect-to-the-internet')
		print('To get help, visit https://community.pantherx.org/')
		print()
		print_debug_qr_code('https://community.pantherx.org/t/pantherx-installation-get-wi-fi-to-work-connect-to-the-internet/72')
		print('Scan to open: https://community.pantherx.org/t/pantherx-installation-get-wi-fi-to-work-connect-to-the-internet/72')
		return False


# def print_wifi_help():
# 	wifi_networks = list_network_interfaces('wifi')

# 	if len(wifi_networks) > 0:
# 		network = wifi_networks[0]
# 		print()
# 		print('######## NEXT STEPS ########')
# 		print()
# 		print('Setup your wireless network like so:')
# 		print('wpa_supplicant -c /root/wpa_supplicant.conf -i {} -B'.format(network.name))
# 		print()
# 		print("If you get an error like 'WLAN soft blocked', try running 'rfkill unblock wifi'")
# 		print()
# 		print('Then, get an IP address:')
# 		print('dhclient -v {}'.format(network.name))

# 	else:
# 		print()
# 		print('######## NEXT STEPS ########')
# 		print()
# 		print('Could not detect a Wi-Fi interface on your computer.')
# 		print('(1) On some devices you need to unblock the inteface with: rfkill unblock wifi')
# 		print('(2) Your Wi-Fi interface is not supported out of the box')
# 		print('=> If anyhow possible, install with a LAN cable.')
# 		print()
# 		print('Consult https://wiki.pantherx.org/Installation-guide/#connect-to-the-internet')
# 		print('To get help, visit https://community.pantherx.org/')
# 		print()
# 		print_debug_qr_code('https://community.pantherx.org/t/pantherx-installation-get-wi-fi-to-work-connect-to-the-internet/72')
# 		print('Scan to open: https://community.pantherx.org/t/pantherx-installation-get-wi-fi-to-work-connect-to-the-internet/72')
		
