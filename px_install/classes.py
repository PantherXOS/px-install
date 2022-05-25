import dataclasses
import json
from dataclasses import dataclass

from .block_devices import BlockDevice


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclass
class SystemConfiguration():
    '''Configuration used for the installation'''
    type: str
    firmware: str
    hostname: str
    timezone: str
    locale: str
    username: str
    password: str
    public_key: str
    disk: BlockDevice
    use_disk_encryption: bool

    def get_dict(self):
        config_dict = {
            'type': self.type,
            'firmware': self.firmware,
            'hostname': self.hostname,
            'locale': self.locale,
            'username': self.username,
            'password': self.password,
            'public_key': self.public_key
        }
        return config_dict

    def get_json(self):
        return json.dumps(self.get_dict())


@dataclass
class RemoteConfig():
    '''Config used for enterprise devices; merges with system configuration and required for device registration'''
    type: str
    timezone: str
    locale: str
    title: str
    location: str
    role: str
    key_security: str
    key_type: str
    domain: str
    host: str
