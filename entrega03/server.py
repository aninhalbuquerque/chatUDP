from protocol import *
from datetime import datetime

try: 
    server = udp_connection()
    server.open_socket('127.0.0.1', 5000, 'server')
    
    while True:
        pkt, client_address, new_connection = server.rdt_recv()
        
        dicio = eval(pkt.decode())
        user = str(server.get_user(client_address))

        n = datetime.now()
        t = n.timetuple()
        y, m, d, h, mi, sec, wd, yd, i = t
        time = str(h) + ':' + str(mi) + ':' +str(sec)

        msg =  str(time) + ' ' + user + ': ' + dicio['data'].decode()
        msg_bye = ''
        msg_list = ''

        if new_connection:
            msg = '----------' + user + ' got in the chat' + '----------'

        if dicio['data'].decode() == 'bye':
            msg_bye = '----------' + user + ' left the chat' + '----------'
            server.disconnect(client_address)
        
        if dicio['data'].decode() == 'list':
            msg_list = server.get_connecteds()
        
        server.send_to_all_clients(msg.encode())
        if msg_bye:
            server.send_to_all_clients(msg_bye.encode())
        if msg_list:
            server.rdt_send(msg_list.encode(), client_address)
    
    server.close_connection()
    

except KeyboardInterrupt:
    server.close_connection()
