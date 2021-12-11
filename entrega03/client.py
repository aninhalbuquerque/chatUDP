from protocol import *
import signal # só funciona em linux

def timeout(signum, frame):
    raise Exception('Seu tempo acabou!')

signal.signal(signal.SIGALRM, timeout)

def try_receive_message():
    try: 
        signal.alarm(2)
        msg_received, address, new_connection = client.rdt_recv()
        signal.alarm(0)
        dicio = eval(msg_received.decode())
        return dicio['data'].decode()

    except Exception:
        return ''

def get_user():
    while True:
        msg = input('type something: ')
        
        if len(msg) < 17:
            continue 
        
        cmd = msg[:16]
        if cmd == 'hi, meu nome eh ':
            return msg[16:]

try:
    client = udp_connection()
    client.open_socket('127.0.0.1', 5000, 'client')

    user = get_user()
    client.rdt_send(user.encode())

    while True:
        if client.has_message():
            msg_received = try_receive_message()
            if msg_received:
                print(msg_received)

        try: 
            signal.alarm(3)
            msg_to_send = input()
            signal.alarm(0)
            while client.has_message():
                msg_received = try_receive_message()
                if msg_received:
                    print(msg_received)
                else:
                    break
            
            client.rdt_send(msg_to_send.encode())

            if msg_to_send == 'bye':
                break
            
        except Exception:
            continue
    
    print(user + ': bye')
    print('\nyou left the chat')
    client.close_connection()

except KeyboardInterrupt:
    while client.has_message():
        msg_received = try_receive_message()
        if msg_received == '':
            break
    
    client.rdt_send('bye'.encode())
    print('\nyou left the chat')
    client.close_connection()

