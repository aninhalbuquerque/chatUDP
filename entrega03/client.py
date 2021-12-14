from protocol import *
import threading
import time

def get_user():
    while True:
        msg = input('type something: ')
        
        if len(msg) < 17:
            continue 
        
        cmd = msg[:16]
        if cmd == 'hi, meu nome eh ':
            return msg[16:]

def thread_recv_msg(client, lock):
    print('Iniciou thread de recv')
    while True:
        try:
            client.sock.settimeout(1)
        except Exception:
            break
        msg_received = ''
        try:
            lock.acquire()
            #print('lock no recv')
            msg_received, address, new_connection = client.rdt_recv()
            lock.release()
            #print('release no recv')

            dicio = eval(msg_received.decode())
            msg_received = dicio['data'].decode()
        except socket.timeout:
            lock.release()
            #print('deu')

        if msg_received:
            print(msg_received)
        time.sleep(1)

def thread_send_msg(client, lock):
    print('Iniciou thread de send')
    while True:
        try :
            msg_to_send = input()
        except EOFError:
            break
        
        lock.acquire()
        #print('lock no send')
        client.rdt_send(msg_to_send.encode())
        lock.release()
        #print('release no send')

        if msg_to_send == 'bye':
            break
    
    print('\nyou left the chat')
    client.close_connection()

client = udp_connection()
client.open_socket('127.0.0.1', 5000, 'client')

user = get_user()
client.rdt_send(user.encode())

lock = threading.Lock()
thread1 = threading.Thread(target=thread_send_msg, args=[client, lock])
thread2 = threading.Thread(target=thread_recv_msg, args=[client, lock])
thread1.start()
thread2.start()
