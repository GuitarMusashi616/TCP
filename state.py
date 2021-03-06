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
        self.tcb = tcp.tcb

    def startup(self):
        raise NotImplementedError

    def open(self):
        raise NotImplementedError

    def send(self):
        raise NotImplementedError

    def receive(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def abort(self):
        raise NotImplementedError

    def status(self):
        raise NotImplementedError

    def download(self, filename):
        raise NotImplementedError

    def upload(self, filename):
        raise NotImplementedError

    def _open_socket(self):
        check_address(self.tcb.source_address)
        self.tcp.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.tcp.socket.bind(self.tcb.source_address)
        self.tcp.socket.settimeout(3)

    def _close_socket(self):
        self.tcp.socket.close()
        self.tcp.socket = None

    def _send_syn(self):
        check_address(self.tcb.source_address)
        check_address(self.tcb.dest_address)
        check_socket(self.tcp.socket)

        h = Header.from_tcb(self.tcb)
        h.SYN = True
        print(h)
        self.tcp.socket.sendto(bytes(h), self.tcb.dest_address)

    def _send_ack(self):
        check_address(self.tcb.source_address)
        check_address(self.tcb.dest_address)
        check_socket(self.tcp.socket)

        h = Header.from_tcb(self.tcb)
        h.ACK = True
        print(h)
        self.tcp.socket.sendto(bytes(h), self.tcb.dest_address)

    def _send_syn_ack(self):
        check_address(self.tcb.source_address)
        check_address(self.tcb.dest_address)
        check_socket(self.tcp.socket)

        h = Header.from_tcb(self.tcb)
        h.SYN = True
        h.ACK = True
        print(h)
        self.tcp.socket.sendto(bytes(h), self.tcb.dest_address)

    def _send_data(self, data):
        check_address(self.tcb.source_address)
        check_address(self.tcb.dest_address)
        check_socket(self.tcp.socket)

        h = Header.from_tcb(self.tcb, 192)
        h.ACK = True
        h.data = data
        print(h)
        self.tcp.socket.sendto(bytes(h), self.tcb.dest_address)

    def _send_fin(self):
        check_address(self.tcb.source_address)
        check_address(self.tcb.dest_address)
        check_socket(self.tcp.socket)

        h = Header.from_tcb(self.tcb)
        h.FIN = True
        print(h)
        self.tcp.socket.sendto(bytes(h), self.tcb.dest_address)

    def _recvfrom_socket(self):
        attempts = 3
        while attempts > 0:
            try:
                header_bytes, addr = self.tcp.socket.recvfrom(1500)
                print(Header(header_bytes))
                return header_bytes, addr
            except (socket.timeout, ConnectionResetError):
                attempts -= 1
        sys.exit("No response from server, shutting down...")

    @classmethod
    def methods(cls) -> Iterable[str]:
        return [x for x, y in cls.__dict__.items() if type(y) == FunctionType]

    def __str__(self):
        return str(type(self)) + ' - ' + str(self.methods())


class Closed(State):
    def startup(self):
        pass

    def open(self):
        self._open_socket()
        if self.tcb.dest_address is None:
            # passive open
            self.tcp.state = Listen(self.tcp)
        else:
            # active open
            self._send_syn()
            self.tcp.state = SynSent(self.tcp)

    def send(self):
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
    def startup(self):
        self.receive()

    def receive(self):
        header_bytes, addr = self._recvfrom_socket()
        header = Header(header_bytes)
        if header.SYN:
            self.tcb.initialize(header, addr)
            self._send_syn_ack()
            self.tcp.state = SynReceived(self.tcp)

    def send(self):
        self._send_syn()
        self.tcp.state = SynSent(self.tcp)

    def close(self):
        self._close_socket()
        self.tcp.state = Closed(self.tcp)


class SynSent(State):
    def startup(self):
        self.receive()

    def close(self):
        self._close_socket()
        self.tcp.state = Closed(self.tcp)

    def receive(self):
        header_bytes, addr = self._recvfrom_socket()
        header = Header(header_bytes)
        if header.SYN and header.ACK:
            self.tcb.initialize(header, addr)
            self._send_ack()
            self.tcp.state = Established(self.tcp)
        elif header.SYN:
            self.tcb.initialize(header, addr)
            self._send_syn_ack()
            self.tcp.state = SynReceived(self.tcp)


class SynReceived(State):
    def startup(self):
        self.receive()

    def receive(self):
        header_bytes, addr = self._recvfrom_socket()
        header = Header(header_bytes)
        if header.ACK:
            self.tcb.sync(header)
            self.tcp.state = Established(self.tcp)

    def close(self):
        self._send_fin()
        self.tcp.state = FinWait1(self.tcp)


class Established(State):
    def startup(self):
        pass

    def close(self):
        self._send_fin()
        self.tcp.state = FinWait1(self.tcp)

    def receive(self):
        header_bytes, addr = self._recvfrom_socket()
        header = Header(header_bytes)
        if header.FIN:
            self.tcb.sync(header)
            self._send_ack()
            self.tcp.state = CloseWait(self.tcp)

    def download(self, filename):
        f = open(filename, 'wb')
        while True:
            header_bytes, addr = self._recvfrom_socket()
            header = Header(header_bytes)
            # print(header)
            if len(header) > 192:
                f.write(header.data)
            else:
                break
        f.close()

    def upload(self, filename):
        f = open(filename, 'rb')
        while True:
            # read file
            data = f.read(1448)

            self._send_data(data)

            # break if last of file
            if len(data) < 1448:
                break

            # wait for ack
            header_bytes, addr = self._recvfrom_socket()
            # print(header)
        f.close()


class FinWait1(State):
    def startup(self):
        self.receive()

    def receive(self):
        header_bytes, addr = self._recvfrom_socket()
        header = Header(header_bytes)
        if header.ACK:
            self.tcb.sync(header)
            self.tcp.state = FinWait2(self.tcp)

        if header.FIN:
            self.tcb.sync(header)
            self._send_ack()
            self.tcp.state = Closing(self.tcp)


class FinWait2(State):
    def startup(self):
        self.receive()

    def receive(self):
        header_bytes, addr = self._recvfrom_socket()
        header = Header(header_bytes)
        if header.FIN:
            self.tcb.sync(header)
            self._send_ack()
            self.tcp.state = TimeWait(self.tcp)


class CloseWait(State):
    def startup(self):
        self.close()

    def close(self):
        self._send_fin()
        self.tcp.state = LastAck(self.tcp)


class LastAck(State):
    def startup(self):
        self.receive()

    def receive(self):
        header_bytes, addr = self._recvfrom_socket()
        header = Header(header_bytes)
        if header.ACK:
            self.tcb.sync(header)
            self.tcp.state = Closed(self.tcp)


class Closing(State):
    def startup(self):
        self.receive()

    def receive(self):
        header_bytes, addr = self._recvfrom_socket()
        header = Header(header_bytes)
        if header.ACK:
            self.tcb.sync(header)
            self.tcp.state = TimeWait(self.tcp)


class TimeWait(State):
    def startup(self):
        # sleep(2*MSL) 2 minute MSL in specification
        self.tcp.state = Closed(self.tcp)
