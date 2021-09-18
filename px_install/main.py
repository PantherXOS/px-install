
from .cli import get_cl_arguments
from .install import installation
from .system_config import exit_if_system_config_exists


def main():
    input_args = get_cl_arguments()
    exit_if_system_config_exists()
    installation(input_args['config'])


if __name__ == '__main__':
    main()
