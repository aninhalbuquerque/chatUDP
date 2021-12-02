from protocol import *

try: 
    server = udp_connection()
    server.open_socket('localhost', 5000, 'server')
    
    while True:
        extension, client_address = server.rdt_recv()
        dicio = eval(extension.decode())

        filename = 'sendByClient_' + str(client_address[1]) + '.' + dicio['data'].decode()
        send_address = client_address
        print('client connected:', client_address[1])

        server.recv_file(filename)

        server.rdt_send(str(send_address[1]).encode(), send_address)

        server.send_file(filename, send_address)

        print('cabou')
    

except KeyboardInterrupt:
    server.close_connection()
