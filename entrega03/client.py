from protocol import *
import signal

def timeout(signum, frame):
    raise Exception('Seu tempo acabou!')

signal.signal(signal.SIGALRM, timeout)

try:
    client = udp_connection()
    client.open_socket('127.0.0.1', 5000, 'client')

    msg = input('digite seu user: ')
    client.rdt_send(msg.encode())

    while True:
        #print('---------------------------------------------')
        if client.sock.recv is not None:
            try: 
                #print('try receive')
                signal.alarm(2)
                msg, address = client.rdt_recv()
                signal.alarm(0)
                dicio = eval(msg.decode())
                print(dicio['data'].decode())
            except Exception as exc:
                x = 0
        
        try: 
            signal.alarm(3)
            msg = input()
            signal.alarm(0)
            client.rdt_send(msg.encode())
        except Exception as exc:
            x = 0


    client.close_connection()

except KeyboardInterrupt:
    client.close_connection()

