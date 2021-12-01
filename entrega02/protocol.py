import socket

class udp_connection:
    serverOpen = True
    seqNumber = 0

    def open_socket(self, ip, port, type):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (ip, port)
        self.type = type
        print(type, 'on')
        if type == 'server':
            self.sock.bind(self.server_address)
            self.sock.settimeout(1)

    def send(self, msg, address = ''):
        if not address:
            address = self.server_address 
        
        return self.sock.sendto(msg, address)

    def receive(self, size):
        return self.sock.recvfrom(size)
    
    def rdt_send(self, msg, address = ''):
        if not address:
            address = self.server_address
        
        pkt = self.make_pkt(msg)
        ack = False 

        while not ack:
            self.send(pkt, address)

            try:
                msg, address = self.receive(4096)
            except socket.timeout:
                print('timeout')
            else:
                ack = self.recv_pkt(msg)
    
    def rdt_recv(self):
            pkt, address = self.receive(4096)


    def send_file(self, filename, address = ''):
        if not address:
            address = self.server_address
        
        print('sending file...')
        file = open(filename, 'rb')
        msg = file.read(2048)
        
        while msg:
            self.rdt_send(msg, address)
            msg = file.read(2048)
        
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
    
    def update_seq_number(self):
        self.seqNumber = (self.seqNumber + 1)%2
    
    def make_pkt(self, msg):
        cksum = 0
        for byte in bytearray(msg):
            cksum ^= byte
        seq = self.seqNumber

        return {
            'checksum': cksum,
            'data': msg,
            'seq': seq
        }
    
    def recv_pkt(self, msg, type='sender'):
        cksum = 0
        for byte in bytearray(msg['data']):
            cksum ^= byte
        
        if cksum != msg['checksum']:
            return False
        
        if type == 'sender' and self.seq != msg['seq']:
            return False

        if type == 'sender':
            self.update_seq_number
        
        return True
