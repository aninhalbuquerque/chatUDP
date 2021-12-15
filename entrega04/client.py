from protocol import *
import threading
from datetime import datetime

def get_user():
    while True:
        msg = input('type something: ')
        
        if len(msg) < 17:
            continue 
        
        cmd = msg[:16]
        if cmd == 'hi, meu nome eh ':
            return msg[16:]

def thread_recv_msg(client, lock):
    while True:
        msg_received = ''
        try:
            pkt, address, time = client.receive(4096)

            if pkt:
                dicio = eval(pkt.decode())
                msg_received = dicio['data'].decode()
                lock.acquire()
                client.add_ack(time, address)
                lock.release()

        except KeyboardInterrupt:
            print('\nyou left the chat')
            client.close_connection()
        except Exception as e:
            #print(e)
            x = 0

        if msg_received:
            print(msg_received)

def thread_send_msg(client, lock):
    while True:
        lock.acquire()
        client.check_buffer()
        lock.release()
        client.check_acks()
        client.check_tosend()

def thread_write_msg(client, lock):
    while True:
        try :
            msg_to_send = input('---> ')
            print("\033[A                             \033[A")
        except EOFError:
            break
        except KeyboardInterrupt:
            msg_to_send = 'bye'
        
        lock.acquire()
        client.add_tosend(msg_to_send.encode())
        lock.release()

        if msg_to_send == 'bye':
            break
    
    print('\nyou left the chat')
    client.close_connection()

try:
    client = udp_connection()
    client.open_socket('127.0.0.1', 5000, 'client')

    #user = get_user()

    lock = threading.Lock()
    thread1 = threading.Thread(target=thread_send_msg, args=[client, lock])
    thread2 = threading.Thread(target=thread_recv_msg, args=[client, lock])
    thread3 = threading.Thread(target=thread_write_msg, args=[client, lock])
    thread1.daemon = True
    thread2.daemon = True
    thread3.daemon = True
    thread1.start()
    thread2.start()
    thread3.start()
    thread1.join()
    thread2.join()
    thread3.join()

except KeyboardInterrupt:
    print('\nyou left the chat')
    client.close_connection()
