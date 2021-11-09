import socket

class udp_connection:
    serverOpen = True

    def open_socket(self, ip, port, type):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (ip, port)
        self.type = type
        print(type, 'on')
        if type == 'server':
            self.sock.bind(self.server_address)

    def send(self, msg, address = ''):
        if not address:
            address = self.server_address 
        
        return self.sock.sendto(msg, address)

    def receive(self, size):
        return self.sock.recvfrom(size)
    
    def send_file(self, filename, address = ''):
        if not address:
            address = self.server_address
        
        print('sending file...')
        file = open(filename, 'rb')
        msg = file.read(4096)
        
        while msg:
            self.send(msg, address)
            msg = file.read(4096)
        
        file.close()
        
        print('done')
        msg = bytes('', "utf8") #pra ele saber que acabou o arquivo
        self.send(msg, address)
    
    def recv_file(self, filename):
        print('receiving file...')
        file = open(filename, 'wb')

        while 1:
            msg, address = self.receive(4096)

            if msg == bytes('', "utf8"):
                break
            
            file.write(msg)
        
        print('done')
        file.close()
    
    def close_connection(self):
        print('\nclosing socket')
        self.sock.close()
