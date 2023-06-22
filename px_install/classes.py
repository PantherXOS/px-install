import dataclasses
import json
from dataclasses import dataclass

from px_install.util import is_valid_hostname, is_valid_timezone

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
    variant: str
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
            'variant': self.variant,
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

    def update_type(self, type: str):
        self.type = type
    
    def update_variant(self, variant: str):
        self.variant = variant

    def update_hostname(self, hostname: str):
        if not is_valid_hostname(hostname):
            raise ValueError('Invalid hostname')
        self.hostname = hostname
    
    def update_timezone(self, timezone: str):
        if not is_valid_timezone(timezone):
            raise ValueError('Invalid timezone')
        self.timezone = timezone

    def update_locale(self, locale: str):
        self.locale = locale

    def update_username(self, username: str):
        self.username = username

    def update_password(self, password: str):
        self.password = password

    def update_public_key(self, public_key: str):
        self.public_key = public_key

    def update_use_disk_encryption(self, encryption: bool):
        self.use_disk_encryption = encryption


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
