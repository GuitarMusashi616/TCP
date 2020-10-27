from main import *

if __name__ == "__main__":
    s = setup_socket(54321)
    while True:
        msg, addr = s.recvfrom(500)
        print(msg, addr)
        s.sendto('received'.encode(), addr)

