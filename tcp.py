import socket
from state import *


class TCP:
    DEST_IP = 'localhost'

    def __init__(self):
        self.socket = None
        self.state = Closed(self)

    @property
    def address(self):
        assert self.socket, "socket must be set up first"
        return self.socket.getsockname()

    def open(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))

    def close(self):
        self.socket.close()
        self.socket = None

    def send(self, header):
        dest_addr = (TCP.DEST_IP, header.dest_port)
        self.socket.sendto(bytes(header), dest_addr)

    def listen(self):
        header_bytes, addr = self.socket.recvfrom(2048)
        return header_bytes, addr


class TCB:
    def __init__(self):
        pass
