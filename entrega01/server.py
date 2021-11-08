from protocol import *

server = udp_connection()
server.open_server(5000)
#server.server_connection()
try: 
    while True:
        msg, client_address = server.server_receive(4096)
        adressAux = client_address
        
        file = open('sendByClient_' + str(client_address[1]) + '.txt', 'wb')
        print('recebendo arquivo de', client_address[1])

        while msg and adressAux == client_address:
            file.write(msg)
            msg, client_address = server.server_receive(4096)
        
        file.close()

except KeyboardInterrupt:
    server.close_connection(server.server)
