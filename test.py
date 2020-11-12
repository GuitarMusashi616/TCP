# Austin Williams
# Shawn Butler
# Computer Networks
# 11 November 2020

# test.py - File used exclusively for unit testing

from tcp import *
from args import *
from config import *
from threading import Thread
from time import sleep
import math
import sys
from socket import timeout
from server import setup_socket


# ssh 137.229.181.232 -l amwilliams24
# 31181318
# cd pycharm/TCP
# python3 /home/A365/tcp/tester.py -f test.py


def test_setup():
    s = setup_socket(12345)


def test_headers():
    header = Header()
    print(header.dest_port)
    print(dir(header))


def test_random():
    header = Header()
    header.destination_port = math.pow(2, 16)
    print(header.destination_port)


def test_closed_state():
    tcp = TCP(('', 12345))
    state = Closed(tcp)
    state2 = State(tcp)
    print(state.methods())
    print(state2.methods())


def simple_setup():
    s = setup_socket(12345)
    ip = 'localhost'
    server_port = 54321

    s.send((ip, server_port), 'hello'.encode())
    print(s.recvfrom(512))


def test_tcp_methods():
    s = setup_socket(54321)
    t1 = Thread(target=TCP.__init__, args=(('', 12345)))
    t2 = Thread(target=s.send, args=(b'hello', ('localhost', 12345)))

    t1.start()
    t2.start()


def test_tcp_address():
    tcp = TCP(('', 12345))
    print(tcp.address)


def test_listening_state():
    tcp = TCP(('', 12345))
    assert isinstance(tcp, Listen)


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
    args = setup_args()
    h = Header.new(args.port, args.server_port, 0, 0)
    h.SYN = True

    tcp = TCP(('', args.port))
    tcp.send(bytes(h), (args.ip, args.server_port))

    header, addr = tcp.receive()
    print(header)
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
    s.sendto(bytes(h), args.dest_address)
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
    sleep(1)
    s.sendto(bytes(h), (args.ip, args.server_port))
    try:
        s.settimeout(3)
        header, addr = s.recvfrom(1500)
        print(addr)
        print(header)
        print(Header(header))
    except (timeout, ValueError, TypeError) as e:
        print(e)


def test_states():
    tcp = TCP(('', 12345), ('127.0.0.1', 54321))
    print(tcp.state)
    tcp.open()
    print(tcp.state)
    tcp.close()
    print(tcp.state)

    tcp2 = TCP(('', 12346))
    print(tcp2.state)
    tcp2.open()
    print(tcp2.state)
    tcp2.close()
    print(tcp2.state)


def test_respond_server():
    tcp = TCP(('', 12345), ('127.0.0.1', 54321))
    tcp.open()
    syn = Header.new(tcp.tcb.source_address[1], tcp.tcb.dest_address[1], 0, 0)
    syn.SYN = True
    tcp.socket.sendto(bytes(syn), tcp.tcb.dest_address)


def test_states_receiving():
    tcp = TCP(('', 12345), ('127.0.0.1', 54321))
    print(tcp.state)
    tcp.open()
    print(tcp.state)
    tcp.receive()
    print(tcp.state)
    # established
    tcp.close()
    print(tcp.state)
    # fin-wait1
    tcp.receive()
    print(tcp.state)
    # fin-wait2
    tcp.receive()
    print(tcp.state)
    # time wait
    tcp.startup()
    print(tcp.state)
    # closed


def automatic_states():
    tcp = TCP(('', 12345), ('127.0.0.1', 54321))
    print(tcp.state)
    # established

    tcp.close()
    print(tcp.state)
    # closed


def automatic_with_args():
    args = setup_args()

    tcp = TCP(('', args.port), (args.ip, args.server_port))
    print(tcp.state)
    if args.mode == 'r':
        tcp.download(args.filename)
    else:
        tcp.upload(args.filename)

    while not isinstance(tcp.state, Closed):
        tcp.receive()


def test_download_sequencing():
    tcp = TCP(('', 12345), ('127.0.0.1', 54321))
    print(tcp.state)
    # established

    tcp.upload('text.txt')


def test_upload_sequencing():
    tcp = TCP(('', 12345), ('127.0.0.1', 54321))
    print(tcp.state)
    # established

    tcp.download('newfile.txt')

def test_upload_repeat():
    tcp = TCP(('', 12345), ('127.0.0.1', 54321))
    print(tcp.state)
    f = open('text.txt', 'rb')

    h = Header()
    h.ACK = True
    h.ack_num = tcp.tcb.RCV_NXT
    h.seq_num = tcp.tcb.SND_NXT
    h.data = f.read(tcp.tcb.SND_WND)

    print_compact(h)
    tcp.socket.sendto(bytes(h), tcp.tcb.dest_address)

    header, addr = tcp.state._recvfrom_socket()
    tcp.tcb.sync_rcv(header)

    print_compact(h)
    tcp.socket.sendto(bytes(h), tcp.tcb.dest_address)
    tcp.tcb.sync_una(h)

    h = Header()
    h.ACK = True
    h.ack_num = tcp.tcb.RCV_NXT
    h.seq_num = tcp.tcb.SND_NXT
    h.data = f.read(tcp.tcb.SND_WND)

    print_compact(h)
    tcp.socket.sendto(bytes(h), tcp.tcb.dest_address)

    f.close()


def test_buffer():
    tcp = TCP(('', 12345), ('127.0.0.1', 54321))
    print(tcp.state)
    f = open('text.txt', 'rb')
    payload = [f.read(MAX_DATA_SIZE), f.read(MAX_DATA_SIZE), f.read(MAX_DATA_SIZE)]

    h = Header()
    h.ACK = True
    h.ack_num = tcp.tcb.RCV_NXT
    h.seq_num = tcp.tcb.SND_NXT + MAX_DATA_SIZE * 2
    h.data = payload[2]

    print_compact(h)
    tcp.socket.sendto(bytes(h), tcp.tcb.dest_address)

    header, addr = tcp.state._recvfrom_socket()
    tcp.tcb.sync_rcv(header)
    
    h = Header()
    h.ACK = True
    h.ack_num = tcp.tcb.RCV_NXT
    h.seq_num = tcp.tcb.SND_NXT + MAX_DATA_SIZE*2
    h.data = payload[2]

    print_compact(h)
    tcp.socket.sendto(bytes(h), tcp.tcb.dest_address)

    header, addr = tcp.state._recvfrom_socket()
    tcp.tcb.sync_rcv(header)

    h = Header()
    h.ACK = True
    h.ack_num = tcp.tcb.RCV_NXT
    h.seq_num = tcp.tcb.SND_NXT + MAX_DATA_SIZE
    h.data = payload[1]

    print_compact(h)
    tcp.socket.sendto(bytes(h), tcp.tcb.dest_address)

    h = Header()
    h.ACK = True
    h.ack_num = tcp.tcb.RCV_NXT
    h.seq_num = tcp.tcb.SND_NXT
    h.data = payload[0]

    print_compact(h)
    tcp.socket.sendto(bytes(h), tcp.tcb.dest_address)

    f.close()


if __name__ == '__main__':
    test_buffer()
    # test_download()
