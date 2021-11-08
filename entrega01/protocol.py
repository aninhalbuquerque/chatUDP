import socket

class udp_connection:
    serverOpen = True

    def open_server(self, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = ('localhost', port)
        self.server.bind(self.server_address)
        print('server on')
    
    def open_client(self, server_ip, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (server_ip, port)

    def server_send(self, msg, address):
        self.server.sendto(msg, address)
    
    def client_send(self, msg):
        self.client.sendto(msg, self.server_address)
    
    def server_receive(self, size):
        msg, client_adress = self.server.recvfrom(size) 
        return msg, client_adress
    
    def client_receive(self, size):
        msg, adress = self.client.recvfrom(size) 
        return msg
    
    def close_connection(self, sock):
        print('\nclosing socket')
        sock.close()
