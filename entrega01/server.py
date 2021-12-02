from protocol import *

try: 
    server = udp_connection()
    server.open_socket('localhost', 5000, 'server')
    
    while True:
        extension, client_address = server.recreive(4096)

        filename = 'sendByClient_' + str(client_address[1]) + '.' + extension.decode()
        send_address = client_address
        print('client connected:', client_address[1])

        server.recv_file(filename)

        server.send(str(send_address[1]).encode(), send_address)

        server.send_file(filename, send_address)

except KeyboardInterrupt:
    server.close_connection()
