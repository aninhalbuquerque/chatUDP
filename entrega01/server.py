from protocol import *

server = udp_connection()
server.open_server(5000)

try: 
    while True:
        msg, client_address = server.server_receive(4096) #receber o oi
        
        filename = 'sendByClient_' + str(client_address[1]) + '.txt'
        send_address = client_address

        file = open(filename, 'wb')
        print('recebendo arquivo de', client_address[1])
        
        while 1:
            msg, client_address = server.server_receive(4096)
            if msg == bytes('', "utf8"):
                break
            
            file.write(msg)
        
        file.close()

        print('devolvendo arquivo de', send_address[1])
        server.server_send(str(send_address[1]).encode(), send_address)

        file = open(filename, 'rb')
        msg = file.read(4096)
        
        while msg:
            server.server_send(msg, send_address)
            msg = file.read(4096)

        print('terminou')
        msg = bytes('', "utf8") #pra ele saber que acabou o arquivo
        server.server_send(msg, send_address)

except KeyboardInterrupt:
    server.close_connection(server.server)
