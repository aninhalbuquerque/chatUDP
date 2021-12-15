from protocol import *
from datetime import datetime
import threading

def get_str(t):
    if t < 10:
        return '0' + str(t)
    
    return str(t)

def thread_recv_msg(server, lock):
    while True:
        msg_received = ''
        user = ''
        try:
            pkt, address, time = server.receive(4096)

            if pkt:
                dicio = eval(pkt.decode())
                msg_received = dicio['data'].decode()
                user = str(server.get_user(address))
                lock.acquire()
                server.add_ack(time, address)
                lock.release()

        except KeyboardInterrupt:
            server.close_connection()
        except Exception as e:
            #print(e)
            x = 0

        if msg_received:
            n = datetime.now()
            t = n.timetuple()
            y, m, d, h, mi, sec, wd, yd, i = t
            time = get_str(h) + ':' + get_str(mi) + ':' + get_str(sec)

            msg =  str(time) + ' ' + user + ': ' + msg_received
            lock.acquire()
            server.add_tosend(msg.encode())
            lock.release()

def thread_send_msg(server, lock):
    while True:
        server.check_buffer()

        server.check_acks()

        server.check_tosend()
        
    
    server.close_connection()

try: 
    server = udp_connection()
    server.open_socket('127.0.0.1', 5000, 'server')

    lock = threading.Lock()
    thread1 = threading.Thread(target=thread_send_msg, args=[server, lock])
    thread2 = threading.Thread(target=thread_recv_msg, args=[server, lock])
    thread1.daemon = True
    thread2.daemon = True
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    
    

except KeyboardInterrupt:
    server.close_connection()
