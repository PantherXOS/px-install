import pathlib

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

VERSION = '0.0.26'
PACKAGE_NAME = 'px-install'
AUTHOR = 'Franz Geffke'
AUTHOR_EMAIL = 'franz@pantherx.org'
URL = 'https://git.pantherx.org/development/applications/px-install'

LICENSE = 'GPLv3+'
DESCRIPTION = 'A command line driven installer with sane defaults.'
LONG_DESCRIPTION = (HERE / "README.md").read_text()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
    'requests',
    'tqdm',
    'pytz',
    'qrcode',
    'py-cpuinfo',
    'urllib3'
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    license=LICENSE,
    author_email=AUTHOR_EMAIL,
    url=URL,
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    package_data={
        "": [
            'templates/base-desktop-bios-ssh.scm',
            'templates/base-desktop-efi-ssh.scm',
            'templates/base-desktop-bios.scm',
            'templates/base-desktop-efi.scm',
            'templates/channels.scm'
        ]
    },
    entry_points={
        'console_scripts': ['px-install=px_install.main:main'],
    },
    packages=find_packages(),
    zip_safe=False
)
