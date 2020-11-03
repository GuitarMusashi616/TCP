import socket
from state import *
from socket import timeout
import random


class TCP:
    def __init__(self, source_address, dest_address=None):
        self.socket = None
        self.tcb = TCB(source_address, dest_address)
        self.state = Closed(self)
        self.open()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state: State):
        assert isinstance(state, State)
        self._state = state
        self._state.startup()

    @property
    def address(self):
        assert self.socket, "tcp socket must be opened first"
        return self.socket.getsockname()

    def startup(self):
        self.state.startup()

    def open(self):
        self.state.open()

    def send(self, header_bytes, address):
        self.socket.send(header_bytes, address)

    def receive(self):
        self.state.receive()

    def close(self):
        self.state.close()

    def abort(self):
        pass

    def status(self):
        pass

    def establish_connection(self):
        pass

    def download(self, filename):
        self.state.download(filename)

    def upload(self, filename):
        self.state.upload(filename)

    def close_connection(self):
        pass


class TCB:
    def __init__(self, source_address, dest_address=None):
        self.source_address = source_address
        self.dest_address = dest_address

        self.SND_UNA = None
        self.SND_NXT = None
        self.SND_WND = None
        self.SND_UP = None
        self.SND_WL1 = None
        self.SND_WL2 = None
        self.ISS = None

        self.RCV_NXT = None
        self.RCV_WND = None
        self.RCV_UP = None
        self.IRS = None

        self.init_sequence_nums()

    def init_sequence_nums(self, window=1448):
        start_num = random.randint(0, 100)  # 2**32-1
        self.ISS = start_num
        self.SND_UNA = start_num
        self.SND_WND = window
        self.SND_NXT = start_num
        self.RCV_NXT = 0

    def initialize(self, header, addr):
        self.dest_address = addr if self.dest_address is None else self.dest_address
        self.RCV_WND = header.window
        self.SND_WND = header.window
        self.RCV_UP = header.urgent_ptr

    def sync_snd(self, header):
        # call right after sending
        if not self.SND_NXT:
            self.SND_NXT = header.seq_num
        self.SND_NXT += header.seq_increment

    def sync_rcv(self, header):
        if not self.RCV_NXT:
            self.RCV_NXT = header.seq_num
        self.RCV_NXT += header.seq_increment

    def check_rcv(self, header):
        if header.seq_num == self.RCV_NXT:
            return True
        return False


    # def sync(self, header, increment=1):
    #     self.RCV_NXT = header.seq_num + increment if not self.RCV_NXT else self.RCV_NXT + increment

    @property
    def ISS(self):
        return self._ISS

    @ISS.setter
    def ISS(self, value):
        if isinstance(value, int):
            self._ISS = value % 2**32
        else:
            self._ISS = value



