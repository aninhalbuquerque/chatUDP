from protocol import *
import threading
import os


def get_user():
    while True:
        msg = input('type something: ')
        
        if len(msg) < 17:
            continue 
        
        cmd = msg[:16]
        if cmd == 'hi, meu nome eh ':
            return msg

def thread_recv_msg(client, lock):
    while True:
        msg_received = ''
        try:
            pkt, address, time = client.receive(4096)

            if pkt:
                dicio = eval(pkt.decode())
                msg_received = dicio['data'].decode()
                lock.acquire()
                client.add_ack(time, msg_received, address)
                lock.release()

        except KeyboardInterrupt:
            x = 0
        except Exception as e:
            #print(e)
            x = 0

        if msg_received:
            print(msg_received)

            if client.bye:
                break

def thread_send_msg(client, lock):
    while True:
        lock.acquire()
        client.check_buffer()
        lock.release()
        sair = client.check_acks()
        if sair:
            break
        client.check_tosend()

def thread_write_msg(client, lock, user):
    while True:
        if user:
            lock.acquire()
            client.add_tosend(user.encode(), '')
            lock.release()

            user = ''
        else:
            try :
                msg_to_send = input()
                print("\033[A                             \033[A")
            except EOFError:
                break
            except KeyboardInterrupt:
                break

            lock.acquire()
            client.add_tosend(msg_to_send.encode(), '')
            lock.release()

            if msg_to_send == 'bye':
                break

try:
    client = udp_connection()
    client.open_socket('127.0.0.1', 5000, 'client')

    user = get_user()
    
    os.system('cls' if os.name == 'nt' else 'clear')

    lock = threading.Lock()
    thread1 = threading.Thread(target=thread_send_msg, args=[client, lock])
    thread2 = threading.Thread(target=thread_recv_msg, args=[client, lock])
    thread3 = threading.Thread(target=thread_write_msg, args=[client, lock, user])
    thread1.daemon = True
    thread2.daemon = True
    thread3.daemon = True
    thread1.start()
    thread2.start()
    thread3.start()
    thread1.join()
    thread2.join()
    thread3.join()

    print('\n---------- you left the chat ----------')
    client.close_connection()

except KeyboardInterrupt:
    print('\n---------- you left the chat ----------')
    client.close_connection()
