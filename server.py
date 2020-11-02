from main import *
from header import *
from tcp import *


def simple():
    s = setup_socket(54321)
    while True:
        msg, addr = s.recvfrom(1500)
        print(msg, addr)
        print(len(msg))
        print(Header(msg))
        s.send(addr, 'received'.encode())


def respond():
    s = setup_socket(54321)
    seq_num = 100
    while True:
        msg, addr = s.recvfrom(1500)
        print(msg, addr)
        print(len(msg))
        h = Header(msg)
        print(h)
        if h.SYN:
            s_addr = s.getsockname()
            ack = Header.new(s_addr[1], addr[1], seq_num, h.seq_num+1)
            ack.SYN = True
            print(ack)
            s.sendto(bytes(ack), addr)


def tcp_listen():
    tcp = TCP(('', 54321))
    print(tcp.state)
    tcp.open()
    print(tcp.state)
    # listen
    tcp.receive()
    print(tcp.state)
    # syn-received
    tcp.receive()
    print(tcp.state)
    # established
    tcp.receive()
    print(tcp.state)
    # close-wait
    tcp.close()
    print(tcp.state)
    # last-ack
    tcp.receive()
    print(tcp.state)
    # closed


def auto_listen():
    tcp = TCP(('', 54321))
    print(tcp.state)
    # established
    tcp.receive()
    print(tcp.state)
    # closed


def receive_upload():
    tcp = TCP(('', 54321))
    print(tcp.state)
    # established
    tcp.receive()
    print(tcp.state)
    # closed


if __name__ == "__main__":
    auto_listen()

