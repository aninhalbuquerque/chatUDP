from protocol import *

try: 
    server = udp_connection()
    server.open_socket('127.0.0.1', 5000, 'server')

    clients = {}
    
    while True:
        pkt, client_address = server.rdt_recv()
        
        dicio = eval(pkt.decode())
        user = str(server.get_user(client_address))
        msg =  user + ': ' + dicio['data'].decode()
        msg_bye = ''

        if dicio['data'].decode() == 'bye':
            msg_bye = '----------' + user + ' left the chat' + '----------'
            server.disconnect(client_address)
        
        server.send_to_all_clients(msg.encode())
        if msg_bye:
            server.send_to_all_clients(msg_bye.encode())
    
    server.close_connection()
    

except KeyboardInterrupt:
    server.close_connection()
