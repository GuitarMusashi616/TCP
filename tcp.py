# Austin Williams
# Shawn Butler
# Computer Networks
# 11 November 2020

# tcp.py - File used to define TCP class, has a state, socket, and tcb.


from state import *
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

    def download(self, filename):
        self.state.download(filename)

    def upload(self, filename):
        self.state.upload(filename)


class TCB:
    def __init__(self, source_address, dest_address=None):
        self.source_address = source_address
        self.dest_address = dest_address

        self.SND_UNA = None
        self.SND_NXT = None
        self.SND_WND = None
        self.SND_UP = None
        # self.SND_WL1 = None
        # self.SND_WL2 = None
        # self.ISS = None

        self.RCV_NXT = None
        self.RCV_WND = None
        self.RCV_UP = None
        # self.IRS = None

        self.init_sequence_nums()

    def init_sequence_nums(self, window=MAX_DATA_SIZE):
        start_num = random.randint(0, 100)  # 2**32-1
        # self.ISS = start_num
        self.SND_UNA = start_num
        self.SND_WND = window
        self.SND_NXT = start_num
        self.RCV_NXT = 0

    def initialize(self, header, addr):
        self.dest_address = addr if self.dest_address is None else self.dest_address
        self.RCV_WND = header.window
        self.SND_WND = header.window
        self.RCV_UP = header.urgent_ptr
        self.sync_rcv(header)

    def sync_una(self, header):
        # call right after sending
        if not self.SND_UNA:
            self.SND_UNA = header.seq_num
        self.SND_UNA += header.seq_increment

    def sync_snd_from_una(self):
        # call right after receiving ack
        self.SND_NXT = self.SND_UNA

    def sync_snd(self, header):
        # call right after receiving ack
        if not self.SND_NXT:
            self.SND_NXT = header.seq_num
        self.SND_NXT += header.seq_increment

    def sync_rcv(self, header):
        if not self.RCV_NXT:
            self.RCV_NXT = header.seq_num
        self.RCV_NXT += header.seq_increment
        self.sync_snd_from_una()

    def check_rcv(self, header):
        if header.seq_num == self.RCV_NXT:
            return True
        return False

    def is_next_seq(self, header):
        if self.RCV_NXT:
            if header.seq_num == self.RCV_NXT:
                return True
            else:
                if PRINT_ERRORS:
                    print(str(header.seq_num) + ' is not next seq number, should be ' + str(self.RCV_NXT))
                return False
        else:
            return True

    def is_next_ack(self, header):
        if self.SND_NXT:
            if header.ack_num == self.SND_UNA:
                return True
            else:
                if PRINT_ERRORS:
                    print(str(header.ack_num) + ' is not next ack number, should be ' + str(self.SND_UNA))
                return False
        else:
            return True

    @property
    def RCV_NXT(self):
        return self._RCV_NXT

    @RCV_NXT.setter
    def RCV_NXT(self, value):
        if isinstance(value, int):
            self._RCV_NXT = value % 2**32
        else:
            self._RCV_NXT = value

    @property
    def SND_NXT(self):
        return self._SND_NXT

    @SND_NXT.setter
    def SND_NXT(self, value):
        if isinstance(value, int):
            self._SND_NXT = value % 2**32
        else:
            self._SND_NXT = value

    @property
    def SND_UNA(self):
        return self._SND_UNA

    @SND_UNA.setter
    def SND_UNA(self, value):
        if isinstance(value, int):
            self._SND_UNA = value % 2 ** 32
        else:
            self._SND_UNA = value

