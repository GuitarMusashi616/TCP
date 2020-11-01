import argparse
import socket
from args import setup_args


def setup_socket(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))
    return s


if __name__ == '__main__':
    # setup the args and the socket
    args = setup_args()
    s = setup_socket(12345)