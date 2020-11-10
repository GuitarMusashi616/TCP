from typing import Iterable
from types import FunctionType
from header import *
import socket
import sys
import time

MSL = 2
VERBOSE = False


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
        if VERBOSE:
            print_compact(h)
        self.tcp.socket.sendto(bytes(h), self.tcb.dest_address)
        self.tcb.sync_snd(h)

    def _send_ack(self):
        check_address(self.tcb.source_address)
        check_address(self.tcb.dest_address)
        check_socket(self.tcp.socket)

        h = Header.from_tcb(self.tcb)
        h.ACK = True
        if VERBOSE:
            print_compact(h)
        self.tcp.socket.sendto(bytes(h), self.tcb.dest_address)
        self.tcb.sync_snd(h)

    def _send_syn_ack(self):
        check_address(self.tcb.source_address)
        check_address(self.tcb.dest_address)
        check_socket(self.tcp.socket)

        h = Header.from_tcb(self.tcb)
        h.SYN = True
        h.ACK = True
        if VERBOSE:
            print_compact(h)
        self.tcp.socket.sendto(bytes(h), self.tcb.dest_address)
        self.tcb.sync_snd(h)

    def _send_data(self, data, is_repeat_send):
        check_address(self.tcb.source_address)
        check_address(self.tcb.dest_address)
        check_socket(self.tcp.socket)

        h = Header.from_tcb(self.tcb)
        h.data = data
        h.ACK = True
        if VERBOSE:
            print_compact(h)
        self.tcp.socket.sendto(bytes(h), self.tcb.dest_address)
        if not is_repeat_send:
            self.tcb.sync_snd(h)

    def _send_fin(self):
        check_address(self.tcb.source_address)
        check_address(self.tcb.dest_address)
        check_socket(self.tcp.socket)

        h = Header.from_tcb(self.tcb)
        h.FIN = True
        if VERBOSE:
            print_compact(h)
        self.tcp.socket.sendto(bytes(h), self.tcb.dest_address)
        self.tcb.sync_snd(h)

    def _recvfrom_socket(self):
        attempts = 3
        while attempts > 0:
            try:
                header_bytes, addr = self.tcp.socket.recvfrom(1500)
                header = Header(header_bytes)
                if VERBOSE:
                    print_compact(header)
                return header, addr
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
        header, addr = self._recvfrom_socket()
        if header.SYN and self.tcb.is_next_seq(header):
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
        header, addr = self._recvfrom_socket()
        if self.tcb.is_next_seq(header):
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
        header, addr = self._recvfrom_socket()
        if header.ACK and self.tcb.is_next_seq(header):
            self.tcb.sync_rcv(header)
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
        header, addr = self._recvfrom_socket()
        if header.FIN and self.tcb.is_next_seq(header):
            self.tcb.sync_rcv(header)
            self._send_ack()
            self.tcp.state = CloseWait(self.tcp)

    def download(self, filename):
        f = open(filename, 'wb')
        is_downloading = True
        while is_downloading:
            header, addr = self._recvfrom_socket()
            self.tcb.sync_rcv(header)
            # print(len(header))
            # print(len(header.data))
            # print(header.window)
            # print(header_bytes)
            # print()
            # print(header)

            if header.data:
                f.write(header.data)
                self._send_ack()
                if len(header.data) < header.window:
                    is_downloading = False
            else:
                is_downloading = False
        f.close()

    def upload(self, filename):
        f = open(filename, 'rb')
        is_uploading = True
        is_repeat_send = False
        data = f.read(self.tcb.SND_WND)
        while is_uploading:
            # read file
            self._send_data(data, is_repeat_send)

            # wait for ack
            header, addr = self._recvfrom_socket()
            if header.ACK and self.tcb.is_next_seq(header):
                self.tcb.sync_rcv(header)
                # break if last of file
                if len(data) < self.tcb.SND_WND:
                    break
                data = f.read(self.tcb.SND_WND)
                is_repeat_send = False
                # print(header)
            elif header.ACK:
                is_repeat_send = True
        f.close()


class FinWait1(State):
    def startup(self):
        self.receive()

    def receive(self):
        header, addr = self._recvfrom_socket()
        if self.tcb.is_next_seq(header):
            if header.ACK:
                self.tcb.sync_rcv(header)
                self.tcp.state = FinWait2(self.tcp)

            if header.FIN:
                self.tcb.sync_rcv(header)
                self._send_ack()
                self.tcp.state = Closing(self.tcp)


class FinWait2(State):
    def startup(self):
        self.receive()

    def receive(self):
        header, addr = self._recvfrom_socket()
        if header.FIN and self.tcb.is_next_seq(header):
            self.tcb.sync_rcv(header)
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
        header, addr = self._recvfrom_socket()
        if header.ACK and self.tcb.is_next_seq(header):
            self.tcb.sync_rcv(header)
            self.tcp.state = Closed(self.tcp)


class Closing(State):
    def startup(self):
        self.receive()

    def receive(self):
        header, addr = self._recvfrom_socket()
        if header.ACK and self.tcb.is_next_seq(header):
            self.tcb.sync_rcv(header)
            self.tcp.state = TimeWait(self.tcp)


class TimeWait(State):
    def startup(self):
        time.sleep(2*MSL)  # 2 minute MSL in specification
        self.tcp.state = Closed(self.tcp)
