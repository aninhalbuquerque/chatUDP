import socket
from struct import unpack

class udp_connection:
    serverOpen = True
    seqNumber = 0
    connecteds = {}

    recebe = 0

    def open_socket(self, ip, port, type):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (ip, port)
        self.type = type
        print(type, 'on')
        if type == 'server':
            self.sock.bind(self.server_address)
        else:
            self.connect('server', self.server_address)
            

    def send(self, msg, address = ''):
        if not address:
            address = self.server_address 
        
        return self.sock.sendto(msg, address)

    def receive(self, size, address = ''):
        if not address:
            return self.sock.recvfrom(size)
        
        return self.sock.recvfrom(size)
    
    def rdt_send(self, msg, address = ''):
        self.sock.settimeout(5)
        if not address:
            address = self.server_address
        
        pkt = self.make_pkt(msg, self.get_seq_number(address))
        
        ack = False 

        while not ack:
            #print('mandando:', pkt.decode(), 'para', str(self.get_user(address)))
            self.send(pkt, address)

            try:
                msg, recv_address = self.receive(4096)
            except socket.timeout:
                print('timeout')
            else:
                msgACK = eval(msg.decode())['data'].decode()
                if recv_address != address or msgACK != 'ACK':
                    continue
                
                ack = self.recv_pkt(msg, address)
                #print('msg:', msg.decode())
                #print('ack:', ack)
        
        self.update_seq_number(address)
        self.sock.settimeout(None)
    
    def rdt_recv(self):
        while True:
            pkt, address = self.sock.recvfrom(4096)
            self.check_connection(pkt, address)
            seq = self.get_seq_number(address)
            not_corrupt = self.recv_pkt(pkt, address, 'receiver')
            if self.recebe < 20:
                #print('recebendo:', pkt.decode(), 'de', str(self.get_user(address)))
                self.recebe += 1
                #print('not corrupt') if not_corrupt else print('corrupt')
            if not_corrupt:
                pkt_ack = self.make_pkt(bytes('ACK', 'utf8'), seq)
                #print('ack:', pkt)
                self.send(pkt_ack, address)
                self.update_seq_number(address)
                return pkt, address
            else:
                self.send(self.make_pkt(bytes('ACK', 'utf8'), 1 - seq), address)
    
    def check_connection(self, pkt, address):
        if address in self.connecteds:
            return True
        
        if pkt:
            dicio = eval(pkt.decode())
            user = dicio['data'].decode()
            self.connect(user, address)
            return True
        else:
            return False
 
    def connect(self, user, address):
        #print('address:', address)
        self.connecteds[address] = {
            'user': user,
            'seqNumber': 0
        }
        print('user', user, 'connected')
    
    def disconnect(self, address):
        if address in self.connecteds:
            del self.connecteds[address]
    
    def send_to_all_clients(self, msg):
        for address in self.connecteds:
            self.rdt_send(msg, address)
    
    def close_connection(self):
        print('\nclosing socket')
        self.sock.close()
    
    def update_seq_number(self, address = ''):
        #print('update seq -', address)
        if not address:
            address = self.server_address
        
        self.connecteds[address]['seqNumber'] = 1 - self.connecteds[address]['seqNumber']
        #print('new seq -', self.connecteds[address]['seqNumber'])
    
    def get_seq_number(self, address = ''):
        if not address:
            address = self.server_address
        
        if address in self.connecteds:
            return self.connecteds[address]['seqNumber']
        else:
            self.connect(address[1], address)
            return self.connecteds[address]['seqNumber']
    
    def get_user(self, address = ''):
        if not address:
            address = self.server_address
        
        if address in self.connecteds:
            return self.connecteds[address]['user']
        else:
            self.connect(address[1], address)
            return self.connecteds[address]['user']

    def make_pkt(self, msg, seq):
        cksum = self.checksum(msg)

        return str({
            'cksum': cksum,
            'data': msg,
            'seq': seq
        }).encode()
    
    def recv_pkt(self, msg, address, type='sender'):
        
        dicio = eval(msg.decode())
        cksum = self.checksum(dicio['data'])
        
        seq = self.get_seq_number(address)

        if cksum != dicio['cksum']:
            return False
        #print('from', self.connecteds[address]['user'])
        #print('msg:', dicio['data'].decode())
        #print('self.seqNumber:', seq)
        #print('seq:           ', dicio['seq'])

        if seq != dicio['seq']:
            return False

        #self.update_seq_number(address)
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

    def has_message(self):
        return self.sock.recv is not None
