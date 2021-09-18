'''Work in progress stuff ...'''
import subprocess
import json

result = subprocess.check_output(['lsblk', '--json'])

print('----')
print(json.loads(result))

devices = json.loads(result)
blockdevices = devices['blockdevices']

for device in blockdevices:
    print('#####')
    print('Device {} with {} of storage'.format(
        device['name'], device['size'])
    )
