from protocol import *

try: 
    server = udp_connection()
    server.open_socket('127.0.0.1', 5000, 'server')

    clients = {}
    
    while True:
        pkt, client_address = server.rdt_recv()
        
        dicio = eval(pkt.decode())
        msg = str(server.get_user(client_address)) + ': ' + dicio['data'].decode()
        server.send_to_all_clients(msg.encode())
    
    server.close_connection()
    

except KeyboardInterrupt:
    server.close_connection()
