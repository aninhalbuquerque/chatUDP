from ctypes import addressof
import socket
from struct import unpack
from datetime import datetime

class udp_connection:
    serverOpen = True
    seqNumber = 0
    connecteds = {}

    buffer = {}
    acks = []
    tosend = []
    delete_buffer = []
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

    def send(self, msg, time, address = ''):
        if not address:
            address = self.server_address 
        
        now = str(datetime.now())
        pkt = ''

        if msg.decode() == 'ACK':
            pkt = self.make_pkt(msg, self.get_seq_number('receive', address), time)
            #print('mandando:', str(pkt), ' para', str(self.get_user(address)))
            self.update_seq_number('receive', address)
        else:
            pkt = self.make_pkt(msg, self.get_seq_number('send', address), now)
            #print('mandando:', str(pkt), ' para', str(self.get_user(address)))
            self.buffer[now] = {
                'pkt': pkt,
                'address': address
            }    

        return self.sock.sendto(pkt, address)

    def receive(self, size):
        msg, recv_address = self.sock.recvfrom(size)
        self.check_connection(msg, recv_address)
        #print('recebendo:', str(msg), ' de', str(self.get_user(recv_address)))
        dic = eval(msg.decode())

        cksum = dic['cksum']
        data = dic['data'].decode()
        seq = dic['seq']
        time = dic['time']

        if data != 'ACK' and self.recv_pkt(msg, recv_address, 'receive'):
            return msg, recv_address, time

        if data == 'ACK' and self.recv_pkt(msg, recv_address, 'send'):
            self.delete_buffer.append(time)
            self.update_seq_number('send', recv_address)
        
        return '', recv_address, time
    
    def check_tosend(self):
        if len(self.tosend):
            item = self.tosend[0]
            
            msg = item[0]
            address = item[1]
            self.send(msg, 0, address)

            self.tosend.pop(0)
    
    def check_buffer(self):
        for time in self.delete_buffer:
            if time in self.buffer:
                del self.buffer[time]

        self.delete_buffer = []
        todelete = []
    
        for time in self.buffer:
            now = datetime.now()
            t = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')
            t = now - t 
            if t.seconds >= 5:
                todelete.append(time)
        
        for time in todelete:
            pkt = self.buffer[time]['pkt']
            address = self.buffer[time]['address']

            del self.buffer[time]

            dic = eval(pkt.decode())
            msg = dic['data']
            self.send(msg, 0, address)

    def check_acks(self):
        if len(self.acks):
            a = self.acks[0]
            
            msg = a[0]
            time = a[1]
            address = a[2]
            self.send(msg, time, address)
            
            self.acks.pop(0)
    
    def add_ack(self, time, address=''):
        if not address:
            address = self.server_address
        
        msg = 'ACK'.encode()
        self.acks.append((msg, time, address))
    
    def check_connection(self, pkt, address):
        if address in self.connecteds:
            return False
        
        if pkt:
            dicio = eval(pkt.decode())
            user = dicio['data'].decode()
            self.connect(user, address)
            return True
        else:
            return False
 
    def connect(self, user, address):
        self.connecteds[address] = {
            'user': user,
            'seqNumber': {
                'send': 0,
                'receive': 0
            }
        }
        if self.type == 'server':
            print('user', user, 'connected')
    
    def disconnect(self, address):
        if address in self.connecteds:
            print(self.connecteds[address]['user'] + ' disconnected')
            del self.connecteds[address]
        
    def get_connecteds(self):
        msg_list = '---- users list ----'
        for address in self.connecteds:
            msg_list += '\n' + str(self.connecteds[address]['user'])

        return msg_list
    
    def add_tosend(self, msg):
        for address in self.connecteds:
            self.tosend.append((msg, address))
    
    def close_connection(self):
        print('\nclosing socket')
        self.sock.close()
    
    def update_seq_number(self, type, address = ''):
        if not address:
            address = self.server_address
        
        self.connecteds[address]['seqNumber'][type] = 1 - self.connecteds[address]['seqNumber'][type]
    
    def get_seq_number(self, type, address = ''):
        if not address:
            address = self.server_address
        
        if address in self.connecteds:
            return self.connecteds[address]['seqNumber'][type]
        else:
            self.connect(address[1], address)
            return self.connecteds[address]['seqNumber'][type]
    
    def get_user(self, address = ''):
        if not address:
            address = self.server_address
        
        if address in self.connecteds:
            return self.connecteds[address]['user']
        else:
            self.connect(address[1], address)
            return self.connecteds[address]['user']

    def make_pkt(self, msg, seq, time):
        cksum = self.checksum(msg)

        return str({
            'cksum': cksum,
            'data': msg,
            'seq': seq,
            'time': time
        }).encode()
    
    def recv_pkt(self, msg, address, type='send'):
        
        dicio = eval(msg.decode())
        cksum = self.checksum(dicio['data'])
        
        seq = self.get_seq_number(type, address)

        if cksum != dicio['cksum']:
            return False

        if seq != dicio['seq']:
            return False

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
