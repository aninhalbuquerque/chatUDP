from protocol import *

client = udp_connection()
client.open_client('localhost', 5000) 

try:
    msg = 'oie'
    client.client_send(msg.encode())

    print('enviando arquivo')
    file = open('files/tslyrics.txt', 'rb')
    msg = file.read(4096)
    
    while msg:
        client.client_send(msg)
        msg = file.read(4096)
    
    file.close()
    
    msg = bytes('', "utf8") #pra ele saber que acabou o arquivo
    client.client_send(msg)

    print('recebendo arquivo')
    msg = client.client_receive(4096).decode()
    filename = 'sendByServer_' + str(msg) + '.txt'
    file = open(filename, 'wb')

    while 1:
        msg = client.client_receive(4096)

        if msg == bytes('', "utf8"):
            print('terminou')
            break
        
        file.write(msg)
    
    file.close()

    client.close_connection(client.client)

except KeyboardInterrupt:
    client.close_connection(client.client)

