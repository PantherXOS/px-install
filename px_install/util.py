'''Misc'''

import os


def check_efi_or_bios():
    '''Check if EFI is supported'''
    if os.path.exists('/sys/firmware/efi'):
        return 'efi'
    else:
        return 'bios'
