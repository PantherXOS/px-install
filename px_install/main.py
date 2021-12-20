import sys

import pkg_resources

from px_install.util import generate_and_print_debug_info, is_online, print_debug_qr_code

from .cli import get_cl_arguments
from .install import installation
from .remote_config import cleanup_enterprise_config
from .system_config import exit_if_system_config_exists

version = pkg_resources.require("px_install")[0].version


def main():
    print('------')
    print('Welcome to PantherX Installation v{}'.format(version))
    print()
    print('For guidance, consult: https://wiki.pantherx.org/Installation-guide')
    print('For help, visit https://community.pantherx.org')
    print('------')

    input_args = get_cl_arguments()
    is_enterprise_config = input_args['is_enterprise_config']

    try:
        # raise NotImplementedError()
        installation(input_args['config'], is_enterprise_config)
    except Exception as err:
        print()
        print('######## ERROR ########')
        print('Something went wrong during the installation:')
        print(err)
        print()
        generate_and_print_debug_info(input_args['config'], version, str(err))
        print()
        print('To get help, visit https://community.pantherx.org/')
        print('Scan the QR code, to easily share your setup-related information.')
    finally:
        if is_enterprise_config:
            cleanup_enterprise_config()


if __name__ == '__main__':
    main()
