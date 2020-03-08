import socket
import threading
import struct

from Config import SERVERIP, SERVERPORT, MSGSIZE, ASCII, MULTICAST


class Client:

    def __init__(self, nickname):
        self.nickname = nickname
        self.server = (SERVERIP, SERVERPORT)
        self.multicast_group = MULTICAST

        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.connect(self.server)
        self.tcp_sock.send(bytes(nickname, 'UTF-8'))

        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind(self.tcp_sock.getsockname())

        self.multicast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.multicast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.multicast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        self.multicast_sock.bind(('', 10000))

        mreq = struct.pack('4sL', socket.inet_aton(self.multicast_group), socket.INADDR_ANY)
        self.multicast_sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        tcp_thread = threading.Thread(target=self.listen_for_msgs_tcp)
        udp_thread = threading.Thread(target=self.listen_for_msgs_udp)
        multi_thread = threading.Thread(target=self.listen_for_msgs_multicast)
        cmds_thread = threading.Thread(target=self.listen_for_cmds)
        tcp_thread.start()
        udp_thread.start()
        multi_thread.start()
        cmds_thread.start()

    def listen_for_msgs_tcp(self):
        try:
            while True:
                buff = self.tcp_sock.recv(MSGSIZE)
                print(str(buff, 'UTF-8'))
        except ConnectionAbortedError:
            print("Goodbye :)")

    def listen_for_msgs_udp(self):
        while True:
            buff, address = self.udp_sock.recvfrom(MSGSIZE)
            print(str(buff, 'UTF-8'))

    def listen_for_msgs_multicast(self):
        while True:
            buff, address = self.multicast_sock.recvfrom(MSGSIZE)
            print(str(buff, 'UTF-8'))

    def listen_for_cmds(self):
        while True:

            command = input()
            if command == "END":
                self.tcp_sock.close()
            elif command == "U":
                msg = input("UDP message: ")
                if msg == "":
                    msg = ASCII
                self.udp_sock.sendto(bytes(msg, "UTF-8"), (SERVERIP, SERVERPORT))
            elif command == "M":
                msg = input("Multicast message: ")
                self.multicast_sock.sendto(bytes(self.nickname + ": " + msg, "UTF-8"), (self.multicast_group, 10000))
                # pass
            else:
                self.tcp_sock.send(bytes(command, 'UTF-8'))


if __name__ == '__main__':
    nickname = input("Tell me your login: ")
    client = Client(nickname)
