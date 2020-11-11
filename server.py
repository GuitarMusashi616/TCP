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


def test_download():
    tcp = TCP(('', 54321))
    print(tcp.state)
    # established
    tcp.download('newfile.txt')
    tcp.receive()
    print(tcp.state)
    # closed


def test_repeat_protocol():
    tcp = TCP(('', 54321))
    print(tcp.state)

    header, addr = tcp.state._recvfrom_socket()
    tcp.tcb.sync_rcv(header)
    print(f'1st data: {header.data[:20]}')

    h = Header()
    h.ACK = True
    h.ack_num = header.seq_num
    h.seq_num = tcp.tcb.SND_NXT

    tcp.socket.sendto(bytes(h), addr)
    tcp.tcb.sync_una(h)

    header2, addr2 = tcp.state._recvfrom_socket()
    tcp.tcb.sync_rcv(header2)
    print(f'2nd data: {header2.data[:20]}')

    i = Header()
    i.ACK = True
    i.ack_num = header.seq_num + len(header.data)
    i.seq_num = tcp.tcb.SND_NXT

    tcp.socket.sendto(bytes(i), addr2)
    tcp.tcb.sync_una(i)


# def test_upload_repeat():
#     tcp = TCP(('', 54321))
#     print(tcp.state)
#     f = open('text.txt', 'rb')
#
#     h = Header()
#     h.data = f.read(50)
#     h.ACK = True
#     h.ack_num = tcp.tcb.RCV_NXT
#     h.seq_num = tcp.tcb.SND_NXT
#
#     tcp.socket.sendto(bytes(h), ('127.0.0.1', 12345))
#
#     header, addr = tcp.state._recvfrom_socket()
#     tcp.tcb.sync_rcv(header)
#
#     tcp.socket.sendto(bytes(h), ('127.0.0.1', 12345))
#
#     header, addr = tcp.state._recvfrom_socket()
#     tcp.tcb.sync_rcv(header)
#
#     tcp.socket.sendto(bytes(h), ('127.0.0.1', 12345))
#     f.close()

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



if __name__ == "__main__":
    test_upload_repeat()

