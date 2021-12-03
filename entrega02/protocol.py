import socket
from struct import unpack

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

    def send(self, msg, address = ''):
        if not address:
            address = self.server_address 
        
        return self.sock.sendto(msg, address)

    def receive(self, size):
        return self.sock.recvfrom(size)
    
    def rdt_send(self, msg, address = ''):
        self.sock.settimeout(1)
        if not address:
            address = self.server_address
        
        pkt = self.make_pkt(msg, self.seqNumber)
        
        ack = False 

        while not ack:
            #print('mandando:', pkt.decode())
            self.send(pkt, address)

            try:
                msg, address = self.receive(4096)
            except socket.timeout:
                print('timeout')
            else:
                ack = self.recv_pkt(msg)
        
        self.sock.settimeout(None)
    
    def rdt_recv(self):
        pkt, address = self.sock.recvfrom(4096)
        #print('recebendo:', pkt.decode())
        not_corrupt = self.recv_pkt(pkt, 'receiver')
        if not_corrupt:
            self.send(self.make_pkt(bytes('ACK', 'utf8'), self.seqNumber), address)
            self.update_seq_number
        else:
            self.send(self.make_pkt(bytes('ACK', 'utf8'), 1 - self.seqNumber))

        return pkt, address

    def send_file(self, filename, address = ''):
        if not address:
            address = self.server_address
        
        print('sending file...')
        file = open(filename, 'rb')
        msg = file.read(1024)
        
        while msg:
            self.rdt_send(msg, address)
            msg = file.read(1024)
        
        file.close()
        
        print('done')
        msg = bytes('bye', 'utf8') #pra ele saber que acabou o arquivo
        self.rdt_send(msg, address)
    
    def recv_file(self, filename):
        print('receiving file...')
        file = open(filename, 'wb')

        while 1:
            msg, address = self.rdt_recv()
            dicio = eval(msg.decode())

            if dicio['data'] == bytes('bye', "utf8"):
                break
            
            file.write(dicio['data'])
        
        print('done')
        file.close()
    
    def close_connection(self):
        print('\nclosing socket')
        self.sock.close()
    
    def update_seq_number(self):
        self.seqNumber = (self.seqNumber + 1)%2
    
    def make_pkt(self, msg, seq):
        cksum = self.checksum(msg)

        return str({
            'cksum': cksum,
            'data': msg,
            'seq': seq
        }).encode()
    
    def recv_pkt(self, msg, type='sender'):
        
        dicio = eval(msg.decode())
        cksum = self.checksum(dicio['data'])
        
        if cksum != dicio['cksum']:
            return False
        
        if type == 'sender' and self.seqNumber != dicio['seq']:
            return False

        if type == 'sender':
            self.update_seq_number
        
        return True
    
    def checksum(self, msg):
        cksum = 0

        array = bytearray(msg)[::-1]
        lenght = len(array)

        for i in range(lenght):
            if i % 2:
                continue 
            
            cksum += (array[i] << 8)
            if i + 1 < lenght:
                cksum += array[i+1]

        while cksum >> 16:
            cksum = (cksum >> 16) + (cksum & 0xffff)
        
        cksum = cksum ^ 0xffff
        return cksum
