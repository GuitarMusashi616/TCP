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

    def download_file(self):
        pass

    def upload_file(self):
        pass

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

    def init_sequence_nums(self, window=5):
        start_num = random.randint(0, 2**32-1)
        self.ISS = start_num
        self.SND_UNA = start_num
        self.SND_WND = window
        self.SND_NXT = start_num

    def sync_tcb(self, header):
        self.RCV_WND = header.window
        self.RCV_NXT = header.seq_num + len(header)
        self.RCV_UP = header.urgent_ptr
        self.IRS = header.seq_num

    @property
    def ISS(self):
        return self._ISS

    @ISS.setter
    def ISS(self, value):
        if isinstance(value, int):
            self._ISS = value % 2**32
        else:
            self._ISS = value



