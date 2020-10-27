import numpy as np
import math
from bitstring import BitArray, BitStream, pack


class HeaderType:
    URG = 0
    ACK = 2
    PSH = 4
    RST = 8
    SYN = 16
    FIN = 32


def to_int(num, bit):
    return int(num) % int(math.pow(2, bit))


class Header:
    def __init__(self, source_port=0, dest_port=0, seq_num=0, ack_num=0, offset=0, reserved=0, control_bits=0, window=0, checksum=0,
                 urgent_ptr=0):
        self._bits = BitArray(256)
        self.source_port = source_port
        self.dest_port = dest_port
        self.seq_num = seq_num
        self.ack_num = ack_num
        self.offset = offset
        self.reserved = reserved
        self.control_bits = control_bits
        self.window = window
        self.checksum = checksum
        self.urgent_ptr = urgent_ptr

    @classmethod
    def from_header(cls, header):
        instance = cls()
        instance.__grid = header
        return instance

    @property
    def source_port(self):
        return self._bits[0:16].uint

    @source_port.setter
    def source_port(self, value):
        self._bits[0:16] = pack('uint:16', value)

    @property
    def dest_port(self):
        return self._bits[16:32].uint

    @dest_port.setter
    def dest_port(self, value):
        self._bits[16:32] = pack('uint:16', value)

    @property
    def seq_num(self):
        return self._bits[32:64].uint

    @seq_num.setter
    def seq_num(self, value):
        self._bits[32:64] = pack('uint:32', value)

    @property
    def ack_num(self):
        return self._bits[64:96].uint

    @ack_num.setter
    def ack_num(self, value):
        self._bits[64:96] = pack('uint:32', value)

    @property
    def offset(self):
        return self._bits[96:100].uint

    @offset.setter
    def offset(self, value):
        self._bits[96:100] = pack('uint:4', value)

    @property
    def reserved(self):
        return self._bits[100:106].uint

    @reserved.setter
    def reserved(self, value):
        self._bits[100:106] = pack('uint:6', value)

    @property
    def control_bits(self):
        return self._bits[106:112].uint

    @control_bits.setter
    def control_bits(self, value):
        self._bits[106:112] = pack('uint:6', value)

    @property
    def window(self):
        return self._bits[112:128].uint

    @window.setter
    def window(self, value):
        self._bits[112:128] = pack('uint:16', value)

    @property
    def checksum(self):
        return self._bits[128:144].uint

    @checksum.setter
    def checksum(self, value):
        self._bits[128:144] = pack('uint:16', value)

    @property
    def urgent_ptr(self):
        return self._bits[144:160].uint

    @urgent_ptr.setter
    def urgent_ptr(self, value):
        self._bits[144:160] = pack('uint:16', value)

    @property
    def options(self):
        if self._bits[160:168].uint == 2 and self._bits[168:176].uint == 4:
            return self._bits[160:168].uint, self._bits[168:176].uint, self._bits[176:192].uint,
        else:
            return self._bits[160:168].uint, 0, 0

    @options.setter
    def options(self, value):
        assert isinstance(value, tuple) and len(value) == 3, "Value must be a tuple of length 3"
        assert value[0] in [0, 1, 2] and value[1] in [0, 2], "Value must be (0,0,0), (1,0,0), or (2,4,*)"

        self._bits[160:168] = pack('uint:8', value[0])
        self._bits[168:176] = pack('uint:8', value[1])
        self._bits[176:192] = pack('uint:16', value[2])

    @property
    def data(self):
        return self._bits[192:].bytes

    def __bytes__(self):
        return self._bits.bytes

    def __repr__(self):
        string = 'Source Port: ' + str(self.source_port)+'\n'
        string += 'Destination Port: ' + str(self.dest_port)+'\n'
        string += 'Sequence Number: ' + str(self.seq_num)+'\n'
        string += 'Ack Number: ' + str(self.ack_num)+'\n'
        string += 'Control Bits: ' + str(self.control_bits)+'\n'
        string += 'Window: ' + str(self.window)+'\n'

        return string

    @classmethod
    def create_syn(cls, dest_addr):
        return Header(dest_port=dest_addr, control_bits=HeaderType.SYN)


def create_header():
    h = Header()
    h.control_bits = HeaderType.SYN



