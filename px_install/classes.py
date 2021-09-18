from dataclasses import dataclass


@dataclass
class SystemConfiguration():
    type: str
    firmware: str
    hostname: str
    timezone: str
    locale: str
    username: str
    password: str
    disk: str


@dataclass
class RemoteConfig():
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
