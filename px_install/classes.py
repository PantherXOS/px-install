from dataclasses import dataclass
import dataclasses, json
import json

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
    disk: str


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
