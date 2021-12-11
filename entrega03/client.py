from protocol import *
import threading

def watchdog():
  raise Exception('Seu tempo acabou!')

def timeout(signum, frame):
    raise Exception('Seu tempo acabou!')

def try_receive_message():
    alarm = threading.Timer(2, watchdog)

    try: 
        print('...esperando rdt_recv...')
        alarm.start()
        msg_received, address = client.rdt_recv()
        alarm.cancel()
        print('...chegou rdt_recv...')
        dicio = eval(msg_received.decode())
        return dicio['data'].decode()

    except Exception:
        return ''


try:
    client = udp_connection()
    client.open_socket('127.0.0.1', 5000, 'client')

    user = input('digite seu user: ')
    client.rdt_send(user.encode())

    while True:
        if client.has_message():
            msg_received = try_receive_message()
            if msg_received:
                print(msg_received)
        
        alarm = threading.Timer(3, watchdog)

        try: 
            print('...esperando input...')
            alarm.start()
            msg_to_send = input()
            alarm.cancel()
            print('...recebeu input...')
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
    print('you left the chat')
    client.close_connection()

except KeyboardInterrupt:
    while client.has_message():
        msg_received = try_receive_message()
        if msg_received == '':
            break
    
    client.rdt_send('bye'.encode())
    print('you left the chat')
    client.close_connection()

