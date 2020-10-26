from typing import Iterable
from types import FunctionType
from packet import *


class State:
    def __init__(self, tcp):
        self.tcp = tcp

    # def handle(self):
    #     raise NotImplementedError

    @classmethod
    def methods(cls) -> Iterable[str]:
        return [x for x, y in cls.__dict__.items() if type(y) == FunctionType]


class Listen(State):
    def __init__(self, tcp):
        super().__init__(tcp)
        tcp.listen()


class Closed(State):
    def active_open(self, dest_addr):
        self.tcp.open()
        syn = Packet.create_syn(dest_addr)
        self.tcp.send(syn)

    def passive_open(self):
        self.tcp.open()
        self.tcp.state = Listen(self.tcp)


class SynSent(State):
    def close(self):
        pass

    def receive_syn(self):
        pass

    def receive_syn_ack(self):
        pass


class SynReceived(State):
    pass


class Established(State):
    pass

