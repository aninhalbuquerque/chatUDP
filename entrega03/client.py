from protocol import *
import threading

def get_user():
    while True:
        msg = input('type something: ')
        
        if len(msg) < 17:
            continue 
        
        cmd = msg[:16]
        if cmd == 'hi, meu nome eh ':
            return msg[16:]

def thread_recv_msg(client, lock):
    #print('Iniciou thread de recv')
    while True:
        msg_received = ''
        try:
            msg_received, address, new_connection = client.rdt_recv()

            dicio = eval(msg_received.decode())
            msg_received = dicio['data'].decode()
        except KeyboardInterrupt:
            print('\nyou left the chat')
            client.close_connection()
        except Exception as e:
            #print(e)
            x = 0

        if msg_received:
            print(msg_received)

def thread_send_msg(client, lock):
    #print('Iniciou thread de send')
    while True:
        try :
            msg_to_send = input()
        except EOFError:
            break
        except KeyboardInterrupt:
            msg_to_send = 'bye'
        
        client.rdt_send(msg_to_send.encode())

        if msg_to_send == 'bye':
            break
    
    print('\nyou left the chat')
    client.close_connection()

try:
    client = udp_connection()
    client.open_socket('127.0.0.1', 5000, 'client')

    user = get_user()
    client.rdt_send(user.encode())

    lock = threading.Lock()
    thread1 = threading.Thread(target=thread_send_msg, args=[client, lock])
    thread2 = threading.Thread(target=thread_recv_msg, args=[client, lock])
    thread1.daemon = True
    thread2.daemon = True
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

except KeyboardInterrupt:
    print('\nyou left the chat')
    client.close_connection()
