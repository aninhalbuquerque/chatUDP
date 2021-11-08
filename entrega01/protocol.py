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
    
    def server_connection(self):
        try:
            msg, client_address = self.server.recvfrom(4096)

            while True:
                print('de', client_address, ':', str(msg,"utf8"))
                msg, client_address = self.server.recvfrom(4096)
        
        except KeyboardInterrupt:
            self.close_connection(self.server)
    
    def client_connection(self):
        try:
            msg = input("digite uma mensagem ('sair' para desconectar): ")
            self.client.sendto(bytes(msg,"utf8"), self.server_address)

            while msg != 'sair':
                msg = input("digite uma mensagem ('sair' para desconectar): ")
                self.client.sendto(bytes(msg,"utf8"), self.server_address)
        
        except KeyboardInterrupt:
            self.close_connection(self.client)

    
    def close_connection(self, sock):
        print('\nclosing socket')
        sock.close()
