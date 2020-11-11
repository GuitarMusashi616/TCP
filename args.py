# Austin Williams
# Shawn Butler
# Computer Networks
# 11 November 2020

# args.py - handles the arguments passed to the program with argparse, exits if args are incorrect

import argparse
import sys


def setup_args():
    """Utilizes argparse to setup and return arguments"""
    parser = argparse.ArgumentParser(description='send files reliably over UDP')

    parser.add_argument('-a',
                        action='store',
                        dest='ip',
                        type=check_ip,
                        help='specify ip address',
                        required=True)

    parser.add_argument('-sp',
                        action='store',
                        dest='server_port',
                        type=check_port,
                        help='specify server port number',
                        required=True)

    parser.add_argument('-f',
                        action='store',
                        dest='filename',
                        help='specify name of file to download / upload',
                        type=check_file,
                        required=True)

    parser.add_argument('-cp',
                        action='store',
                        dest='port',
                        type=check_port,
                        help='specify port number',
                        required=True)

    parser.add_argument('-m',
                        action='store',
                        dest='mode',
                        required=False,
                        choices=['r', 'w'],
                        help='r = read from server, w = write to server')

    parser.add_argument('-k',
                        action='store',
                        dest='unknown',
                        type=int,
                        help='specify unknown number',
                        required=False)

    return parser.parse_args()


def check_port(string: str) -> int:
    """Used in setup_args to exit on incorrect ports"""
    try:
        value = int(string)
        assert 5000 <= value <= 65535, "ports must be within the range [5000, 65535]"
    except ValueError:
        sys.exit("ports must be an integer value")
    except AssertionError as e:
        sys.exit(e)
    return value


def check_ip(string: str) -> str:
    """Used in setup_args to exit if ip is incorrect"""
    if string == 'localhost':
        return string
    try:
        ip_bytes = string.split('.')
        assert len(ip_bytes) == 4, 'IP must contain 4 integers separated by "." when not localhost'
        for byte in ip_bytes:
            assert 0 <= int(byte) <= 255, 'integers in IP must be within the range [0,255]'
    except ValueError:
        sys.exit('IP must contain integers separated by "." when not localhost')
    except AssertionError as e:
        sys.exit(e)
    return string


def check_file(string: str) -> str:
    """Used in setup_args to exit if filename is a directory"""
    assert isinstance(string, str), "Filename must be a string of characters"
    if string[-1] == '/':
        sys.exit('Filename must specify a file, not a directory')
    return string


if __name__ == '__main__':
    args = setup_args()
    print(args)