import socket

class udp_connection:
    serverOpen = True
    seqNumber = 0

    def checksum(data):
        pos = len(data)
        if (pos & 1):
            pos -= 1
            sum = ord(data[pos])
        else:
            sum = 0

        while pos > 0:
            pos -= 2
            sum += (ord(data[pos + 1]) << 8) + ord(data[pos])

        sum = (sum >> 16) + (sum & 0xffff)
        sum += (sum >> 16)

        result = (~ sum) & 0xffff
        result = result >> 8 | ((result & 0xff) << 8)
        return chr(result / 256) + chr(result % 256)

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
        checksum = self.recv_pkt(pkt, 'receiver')
        if checksum:
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
        cksum = 0
        for byte in msg:
            cksum ^= byte

        return str({
            'cksum': cksum,
            'data': msg,
            'seq': seq
        }).encode()
    
    def recv_pkt(self, msg, type='sender'):
        cksum = 0
        dicio = eval(msg.decode())

        for byte in bytearray(dicio['data']):
            cksum ^= byte
        
        if cksum != dicio['cksum']:
            return False
        
        if type == 'sender' and self.seqNumber != dicio['seq']:
            return False

        if type == 'sender':
            self.update_seq_number
        
        return True
