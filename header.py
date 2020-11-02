import numpy as np
import math
from bitstring import BitArray, BitStream, pack


class Header:
    def __init__(self, bits=None):
        self._bits = BitArray(160) if bits is None else BitArray(bits)
        max_bits = 192 if len(self._bits) > 192 else len(self._bits)
        self.offset = max_bits // 32

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
    def URG(self):
        return self._bits[106]

    @URG.setter
    def URG(self, value):
        self._bits[106] = pack('uint:1', value)

    @property
    def ACK(self):
        return self._bits[107]

    @ACK.setter
    def ACK(self, value):
        self._bits[107] = pack('uint:1', value)

    @property
    def PSH(self):
        return self._bits[108]

    @PSH.setter
    def PSH(self, value):
        self._bits[108] = pack('uint:1', value)

    @property
    def RST(self):
        return self._bits[109]

    @RST.setter
    def RST(self, value):
        self._bits[109] = pack('uint:1', value)

    @property
    def SYN(self):
        return self._bits[110]

    @SYN.setter
    def SYN(self, value):
        self._bits[110] = pack('uint:1', value)

    @property
    def FIN(self):
        return self._bits[111]

    @FIN.setter
    def FIN(self, value):
        self._bits[111] = pack('uint:1', value)

    @property
    def control_bits(self):
        return self._bits[106:112].uint

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

    @data.setter
    def data(self, value):
        self._bits = self._bits[:192] + BitArray(value)

    def __len__(self):
        return len(self._bits)

    def __bytes__(self):
        return self._bits.bytes

    def __repr__(self):

        string = 'Source Port: ' + str(self.source_port) + '\n\n'
        string += 'Destination Port: ' + str(self.dest_port) + '\n\n'
        string += 'Sequence Number: ' + str(self.seq_num) + '\n\n'
        string += 'Ack Number: ' + str(self.ack_num) + '\n\n'
        string += 'Offset: ' + str(self.offset) + '\n\n'
        string += 'Reserved: ' + str(self.reserved) + '\n\n'
        string += 'Control Bits: ' + '\n'
        string += '\tURG: ' + str(self.URG) + '\n'
        string += '\tACK: ' + str(self.ACK) + '\n'
        string += '\tPSH: ' + str(self.PSH) + '\n'
        string += '\tRST: ' + str(self.RST) + '\n'
        string += '\tSYN: ' + str(self.SYN) + '\n'
        string += '\tFIN: ' + str(self.FIN) + '\n\n'
        string += 'Window: ' + str(self.window) + '\n\n'
        string += 'Checksum: ' + str(self.checksum) + '\n\n'
        string += 'Urgent Pointer: ' + str(self.urgent_ptr) + '\n\n'
        if len(self._bits) > 160:
            string += 'Options: ' + str(self.options) + '\n\n'
            string += 'Data: ' + str(self.data) + '\n'

        return string

    @classmethod
    def new(cls, source_port, dest_port, seq_num, ack_num):
        h = Header()
        h.source_port = source_port
        h.dest_port = dest_port
        h.seq_num = seq_num
        h.ack_num = ack_num
        return h

    @classmethod
    def from_tcb(cls, tcb, size=160):
        try:
            h = Header(size)
            h.source_port = tcb.source_address[1]
            h.dest_port = tcb.dest_address[1]
            h.seq_num = tcb.SND_NXT
            h.ack_num = tcb.RCV_NXT
            h.window = tcb.SND_WND

            tcb.SND_NXT += 1
            # todo: make it increase by num bits
            return h

        except (AttributeError, TypeError) as e:
            print("tcb could not create header from tcb", str(e))




