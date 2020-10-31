from main import *
from header import *
from state import *
from multithreaded import *
from tcp import *
from args import *
from threading import Thread, Event
from time import sleep
import math
import sys


# ssh 137.229.181.232 -l amwilliams24
# 31181318
# cd pycharm/TCP
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


def test_tcp_download():
    sleep(5)
    args = setup_args()
    h = Header()
    h.SYN = True
    h.source_port = args.port
    h.dest_port = args.server_port
    h.seq_num = 0
    h.ack_num = 0

    tcp = TCP()
    tcp.open(args.port)
    tcp.send((args.ip, args.server_port), h)
    header_bytes, addr = tcp.listen()
    print(header_bytes)
    print(addr)


def test_multithread_download():
    args = setup_args()
    h = Header()
    h.SYN = True
    h.source_port = args.port
    h.dest_port = args.server_port
    h.seq_num = 0
    h.ack_num = 0

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', args.port))
    inbox = []
    send(s, args, bytes(h), inbox)
    for s in inbox:
        print(s)
        print()


def test_download():
    args = setup_args()
    h = Header()
    h.SYN = True
    h.source_port = args.port
    h.dest_port = args.server_port
    h.seq_num = 0
    h.ack_num = 0

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', args.port))
    s.sendto(bytes(h), (args.ip, args.server_port))
    try:
        s.settimeout(3)
        s.recvfrom(1500)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    test_download()
