import socket
from state import *


class TCP:
    def __init__(self):
        self.socket = None
        self.state = Closed(self)

    @property
    def address(self):
        assert self.socket, "tcp socket must be opened first"
        return self.socket.getsockname()

    def open(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))

    def close(self):
        self.socket.close()
        self.socket = None

    def send(self, address, header):
        self.socket.sendto(bytes(header), address)

    def listen(self):
        header_bytes, addr = self.socket.recvfrom(2048)
        return header_bytes, addr


class TCB:
    def __init__(self):
        pass



