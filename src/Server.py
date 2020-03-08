import socket
import threading

from Config import SERVERIP, SERVERPORT, MSGSIZE
from ClientData import ClientData


class Server:

    def __init__(self):

        self.client_data_set = {}

        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_sock.bind((SERVERIP, SERVERPORT))

        self.tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_sock.bind((SERVERIP, SERVERPORT))
        self.tcp_sock.listen(5)

        conn_thread = threading.Thread(target=self.listen_for_conns)
        conn_thread.start()
        udp_thread = threading.Thread(target=self.listen_for_msgs)
        udp_thread.start()

    def listen_for_conns(self):
        while True:
            connection, address = self.tcp_sock.accept()

            nickname = connection.recv(MSGSIZE)
            print(str(nickname, 'UTF-8') + " joined the chat")
            self.client_data_set[address] = ClientData(connection, address, str(nickname, 'UTF-8'))

            threading.Thread(target=self.single_connection, args=(connection, address)).start()

    def single_connection(self, connection, address):
        try:
            while True:
                data = connection.recv(MSGSIZE)

                if not data:
                    break

                data = self.client_data_set[address].nickname + ": " + str(data, 'UTF-8')
                print(data)

                for client in self.client_data_set.values():
                    if not client.address[1] == address[1]:
                        client.connection.send(bytes(data, 'UTF-8'))
        except ConnectionResetError:
            dsc_client = self.client_data_set.pop(address)
            print(dsc_client.nickname + " left the chat")

    def listen_for_msgs(self):
        while True:
            data, address = self.udp_sock.recvfrom(MSGSIZE)

            data = self.client_data_set[address].nickname + ": " + str(data, 'UTF-8')
            print(data)

            for client in self.client_data_set.values():
                if not client.address[1] == address[1]:
                    self.udp_sock.sendto(bytes(data, 'UTF-8'), client.address)


if __name__ == '__main__':
    server = Server()
