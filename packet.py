import numpy as np
import math


class PacketType:
    URG = 0
    ACK = 2
    PSH = 4
    RST = 8
    SYN = 16
    FIN = 32


def to_int(num, bit):
    return int(num) % math.pow(2, bit)


class Packet:
    def __init__(self, source_port=0, dest_port=0, seq_num=0, ack_num=0, offset=0, reserved=0, control_bits=0, window=0, checksum=0,
                 urgent_ptr=0, options=0, padding=0, data=0):

        self.source_port = to_int(source_port, bit=16)
        self.dest_port = to_int(dest_port, bit=16)
        self.seq_num = to_int(seq_num, bit=32)
        self.ack_num = to_int(ack_num, bit=32)
        self.offset = to_int(offset, bit=4)
        self.reserved = to_int(reserved, bit=6)
        self.control_bits = to_int(control_bits, bit=6)
        self.window = to_int(window, bit=16)
        self.checksum = to_int(checksum, bit=16)
        self.urgent_ptr = to_int(urgent_ptr, bit=16)
        self.options = options
        self.padding = padding
        self.data = data

    @classmethod
    def create_syn(cls, dest_addr):
        return Packet(dest_port=dest_addr, control_bits=PacketType.SYN)
