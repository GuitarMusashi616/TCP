from main import *
from header import *

if __name__ == "__main__":
    s = setup_socket(54321)
    while True:
        msg, addr = s.recvfrom(500)
        print(msg, addr)
        print(len(msg))
        print(Header(msg))
        s.sendto('received'.encode(), addr)

