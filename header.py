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
        self.__bits = BitArray(256)
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
        return self.__bits[0:16].int

    @source_port.setter
    def source_port(self, value):
        self.__bits[0:16] = pack('uint:16', value)

    @property
    def dest_port(self):
        return self.__bits[16:32].int

    @dest_port.setter
    def dest_port(self, value):
        self.__bits[16:32] = pack('uint:16', value)

    @property
    def seq_num(self):
        return self.__bits[32:64].int

    @seq_num.setter
    def seq_num(self, value):
        self.__bits[32:64] = pack('uint:32', value)

    @property
    def ack_num(self):
        return self.__bits[64:96].int

    @ack_num.setter
    def ack_num(self, value):
        self.__bits[64:96] = pack('uint:32', value)

    @property
    def offset(self):
        return self.__bits[96:100].int

    @offset.setter
    def offset(self, value):
        self.__bits[96:100] = pack('uint:4', value)

    @property
    def reserved(self):
        return self.__bits[100:106].int

    @reserved.setter
    def reserved(self, value):
        self.__bits[100:106] = pack('uint:6', value)

    @property
    def control_bits(self):
        return self.__bits[106:112].int

    @control_bits.setter
    def control_bits(self, value):
        self.__bits[106:112] = pack('uint:6', value)

    @property
    def window(self):
        return self.__bits[112:128].int

    @window.setter
    def window(self, value):
        self.__bits[112:128] = pack('uint:16', value)

    @property
    def checksum(self):
        return self.__bits[128:144].int

    @checksum.setter
    def checksum(self, value):
        self.__bits[128:144] = pack('uint:16', value)

    @property
    def urgent_ptr(self):
        return self.__bits[144:160].int

    @urgent_ptr.setter
    def urgent_ptr(self, value):
        self.__bits[144:160] = pack('uint:16', value)

    @property
    def options(self):
        if self.__bits[160:168].int == 2 and self.__bits[168:176].int == 4:
            return self.__bits[160:168].int, self.__bits[168:176].int, self.__bits[176:192].int,
        else:
            return self.__bits[160:168].int, 0, 0

    @options.setter
    def options(self, value):
        assert isinstance(value, tuple) and len(value) == 3, "Value must be a tuple of length 3"
        assert value[0] in [0, 1, 2] and value[1] in [0, 2], "Value must be (0,0,0), (1,0,0), or (2,4,*)"

        self.__bits[160:168] = pack('uint:8', value[0])
        self.__bits[168:176] = pack('uint:8', value[1])
        self.__bits[176:192] = pack('uint:16', value[2])

    @property
    def data(self):
        return self.__bits[192:].bytes

    def __bytes__(self):
        return self.__bits.bytes

    def __repr__(self):
        string = f"Source Port: {self.source_port}\n"
        string += f"Destination Port: {self.dest_port}\n"
        string += f"Sequence Number: {self.seq_num}\n"
        string += f"Ack Number: {self.ack_num}\n"
        string += f"Control Bits: {self.control_bits}\n"
        string += f"Window: {self.window}\n"

        return string

    @classmethod
    def create_syn(cls, dest_addr):
        return Header(dest_port=dest_addr, control_bits=HeaderType.SYN)


def create_header():
    h = Header()
    h.control_bits = HeaderType.SYN



