# Austin Williams
# Shawn Butler
# Computer Networks
# 11 November 2020

# tcp_client.py - File intended to be run by Dr. Butler's test server

from args import setup_args
from tcp import TCP
from state import Closed


def main():
    args = setup_args()

    tcp = TCP(('', args.port), (args.ip, args.server_port))
    print(tcp.state)
    if args.mode == 'r':
        tcp.download(args.filename)
    else:
        tcp.upload(args.filename)

    while not isinstance(tcp.state, Closed):
        tcp.receive()


if __name__ == '__main__':
    main()