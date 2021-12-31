
import json
import subprocess
from dataclasses import dataclass
from typing import List

from px_install.util import convert_size_string


@dataclass
class BlockDevicePartition():
    type: str
    name: str
    size: float
    dev_name: str

    def __init__(self, type: str, name: str, size: float):
        self.type = type
        self.name = name
        self.size = size
        self.dev_name = '/dev/{}'.format(name)


@dataclass
class BlockDevice():
    type: str
    name: str
    size: float
    partitions: List[BlockDevicePartition]
    dev_name: str

    def __init__(self, type: str, name: str, size: float, partitions: List[BlockDevicePartition] = []):
        self.type = type
        self.name = name
        self.size = size
        self.partitions = partitions
        self.dev_name = '/dev/{}'.format(self.name)

    def reload(self):
        update = get_block_device_by_name(self.name)
        if update is not None:
            self.type = update.type
            self.size = update.size
            self.partitions = update.partitions
        else:
            print('Could not reload block device {} info.'.format(self.dev_name))

    def size_in_gb(self):
        '''Get the size in GB'''
        return self.size / 1000

    def get_partition_dev_name(self, number: int):
        '''
        Get partition dev name; ex: /dev/sda1

        params:
            number: 1, 2, 3, ..
        '''
        partition = "{}{}".format(self.dev_name, number)
        if self.name.startswith('nvme'):
            partition = '{}p{}'.format(self.dev_name, number)
        return partition

    def is_valid_partition(self, dev_name: str):
        '''
        Checks whether patition exists
        
        params:
            dev_name: /dev/sda1, /dev/nvme0n1p1, ...

        '''
        # Do not reload automatically; it might be triggered too frequently
        # => Use manually instead
        # self.reload()
        is_valid = False
        if len(self.partitions) > 0:
            for partition in self.partitions:
                if partition.dev_name == dev_name:
                    is_valid = True
                else:
                    print('Partition {} does not exist on disk {}.'.format(dev_name, self.name))
        return is_valid


valid_block_device_names = [
    'hda', 'hdb', 'hdc', 'hde',
    'sda', 'sdb', 'sdc', 'sde',
    'nvme0n1', 'nvme1n1', 'nvme2n1', 'nvme3n1'
]


def get_block_devices(stout=None):
    '''
    List all attached block devices

    params:
        stout: this is mostly for testing
    '''
    result = None
    if stout is None:
        process = subprocess.run(['lsblk', '--json'], capture_output=True, text=True)
        result = json.loads(process.stdout)
    else:
        result = json.loads(stout)
    
    devices = []
    if 'blockdevices' in result:
        devices = result['blockdevices']

    valid_devices = []
    for device in devices:
        if device['name'] in valid_block_device_names:
            partitions = []
            if 'children' in device:
                for partition in device['children']:
                    partitions.append(BlockDevicePartition(
                        type=partition['type'],
                        name=partition['name'],
                        size=convert_size_string(partition['size']),
                    ))
            valid_devices.append(
                BlockDevice(
                    type=device['type'],
                    name=device['name'],
                    size=convert_size_string(device['size']),
                    partitions=partitions
                )
            )
        else:
            print('Skipping block device {}.'.format(device['name']))

    return valid_devices


def print_block_devices(devices: List[BlockDevice]):
    count = len(devices)
    if count > 0:
        print('Found {}x disk(s):'.format(count))
        for device in devices:
            if device.size_in_gb() > 19:
                print('/dev/{} ({}GB)'.format(device.name, device.size_in_gb()))
            else:
                print('/dev/{} ({}GB) <- Disk is too small: Minimum should be 19GB'.format(device.name, device.size_in_gb()))
    else:
        print('Found no hard disk')


def get_largest_valid_block_device(devices: List[BlockDevice]):
    largest_device = None
    for device in devices:
        if largest_device is None:
            largest_device = device
        if largest_device.size < device.size:
            largest_device = device

    return largest_device


def get_block_device_by_name(name: str, stout=None):
    '''
    List all attached block devices

    params:
        name: should be formatted '/dev/...'
        stout: this is mostly for testing
    '''
    devices = []
    if stout is None:
        devices = get_block_devices()
    else:
        devices = get_block_devices(stout)

    match = None

    print('Found {} block device(s).'.format(len(devices)))

    for device in devices:
        formatted_name = '/dev/{}'.format(device.name)
        if name == formatted_name:
            match = device

    return match
