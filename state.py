from typing import Iterable
from types import FunctionType
from header import *
import socket
import sys


def check_address(address):
    assert isinstance(address, tuple) and len(address) == 2, "address must consist of (ip, port)"


def check_socket(socket):
    assert socket, "tcp socket must be open when sending syn"


class State:
    def __init__(self, tcp):
        self.tcp = tcp

    def startup(self):
        raise NotImplementedError

    def open(self):
        raise NotImplementedError

    def send_syn(self):
        raise NotImplementedError

    def receive(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def abort(self):
        raise NotImplementedError

    def status(self):
        raise NotImplementedError

    def _open_socket(self):
        check_address(self.tcp.source_address)
        self.tcp.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp.socket.bind(self.tcp.source_address)
        self.tcp.socket.settimeout(3)

    def _close_socket(self):
        self.tcp.socket.close()
        self.tcp.socket = None

    def _send_syn(self):
        check_address(self.tcp.source_address)
        check_address(self.tcp.dest_address)
        check_socket(self.tcp.socket)

        _, port = self.tcp.source_address
        ip, server_port = self.tcp.dest_address

        h = Header.new(port, server_port, 0, 0)
        h.SYN = True
        self.tcp.socket.sendto(bytes(h), self.tcp.dest_address)

    def _send_syn_ack(self):
        check_address(self.tcp.source_address)
        check_address(self.tcp.dest_address)
        check_socket(self.tcp.socket)

        _, port = self.tcp.source_address
        ip, server_port = self.tcp.dest_address

        h = Header.new(port, server_port, 0, 0)
        h.SYN = True
        h.ACK = True
        self.tcp.socket.sendto(bytes(h), self.tcp.dest_address)

    def _recvfrom_socket(self):
        attempts = 3
        while attempts > 0:
            try:
                header_bytes, addr = self.tcp.socket.recvfrom(1500)
                return header_bytes, addr
            except socket.timeout:
                attempts -= 1
        sys.exit("No response from server, shutting down...")

    @classmethod
    def methods(cls) -> Iterable[str]:
        return [x for x, y in cls.__dict__.items() if type(y) == FunctionType]

    def __str__(self):
        return str(type(self)) + ' - ' + str(self.methods())


class Closed(State):
    def startup(self):
        self.open()

    def open(self):
        self._open_socket()
        if self.tcp.dest_address is None:
            # passive open
            self.tcp.state = Listen(self.tcp)
        else:
            # active open
            self._send_syn()
            self.tcp.state = SynSent(self.tcp)

    def send_syn(self):
        print("Current state does not support this method")

    def receive(self):
        print("Current state does not support this method")

    def close(self):
        print("Current state does not support this method")

    def abort(self):
        print("Current state does not support this method")

    def status(self):
        print("Current state does not support this method")


class Listen(State):
    def receive(self):
        header_bytes, addr = self._recvfrom_socket()
        header = Header(header_bytes)
        if header.SYN:
            self._send_syn_ack()
            self.tcp.state = SynReceived(self.tcp)

    def send_syn(self):
        self._send_syn()
        self.tcp.state = SynSent(self.tcp)

    def close(self):
        self._close_socket()
        self.tcp.state = Closed(self.tcp)


class SynSent(State):
    def close(self):
        self._close_socket()
        self.tcp.state = Closed(self.tcp)

    def receive(self):
        header_bytes, addr = self._recvfrom_socket()
        header = Header(header_bytes)
        if header.SYN:
            self._send_syn_ack()
            self.tcp.state = SynReceived(self.tcp)


class SynReceived(State):
    pass


class Established(State):
    pass
