from main import *
from header import *
from state import *
from tcp import *
from args import *
from threading import Thread, Event
import math
import sys


# ssh 137.229.181.232 -l amwilliams24
# 31181318
# python3 /home/A365/tcp/tester.py -f test.py


def test_setup():
    s = setup_socket()


def test_headers():
    header = Header()
    print(header.dest_port)
    print(dir(header))


def test_random():
    header = Header()
    header.destination_port = math.pow(2, 16)
    print(header.destination_port)


def simple_handshake():
    pass


def test_closed_state():
    tcp = TCP()
    state = Closed(tcp)
    state2 = State(tcp)
    print(state.methods())
    print(state2.methods())


def simple_setup():
    s = setup_socket(12345)
    ip = 'localhost'
    server_port = 54321

    s.sendto('hello'.encode(), (ip, server_port))
    print(s.recvfrom(512))


def test_tcp_methods():
    tcp = TCP()
    tcp.open(12345)
    s = setup_socket(54321)
    t1 = Thread(target=tcp.listen, args=())
    t2 = Thread(target=s.sendto, args=(b'hello', ('localhost', 12345)))

    t1.start()
    t2.start()


def test_tcp_address():
    tcp = TCP()
    tcp.open(12345)
    print(tcp.address)


def test_listening_state():
    tcp = TCP()
    tcp.state = Listen(tcp.state)


def print_args():
    print(sys.argv)


def test_args():
    args = setup_args()
    filename = args.filename
    sp = args.server_port
    cp = args.port
    mode = args.mode
    unknown = args.unknown
    print(filename, sp, cp, unknown, mode)


def test_download():
    Header()


if __name__ == '__main__':
    test_args()
