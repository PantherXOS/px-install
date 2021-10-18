import pkg_resources

from .cli import get_cl_arguments
from .install import installation
from .system_config import exit_if_system_config_exists
from .remote_config import cleanup_enterprise_config

version = pkg_resources.require("px_install")[0].version


def main():
    print('------')
    print('Welcome to PantherX Installation v{}'.format(version))
    print('------')

    input_args = get_cl_arguments()
    is_enterprise_config = input_args['is_enterprise_config']

    exit_if_system_config_exists()
    installation(input_args['config'], is_enterprise_config)

    if is_enterprise_config:
        cleanup_enterprise_config()


if __name__ == '__main__':
    main()
