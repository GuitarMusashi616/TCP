import socket
from state import *
from socket import timeout


class TCP:
    def __init__(self, source_address, dest_address=None):
        self.source_address = source_address
        self.dest_address = dest_address
        self.socket = None
        self.tcb = None
        self.state = Closed(self)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state: State):
        assert isinstance(state, State)
        self._state = state

    @property
    def address(self):
        assert self.socket, "tcp socket must be opened first"
        return self.socket.getsockname()

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
    def __init__(self):
        pass



