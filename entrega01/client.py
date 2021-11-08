from protocol import *

client = udp_connection()
client.open_client('localhost', 5000)
#client.client_connection()

try:
    print('enviando arquivo')
    file = open('file.txt', 'rb')
    msg = file.read(4096)

    while msg:
        client.client_send(msg)
        msg = file.read(4096)

    client.close_connection(client.client)

except KeyboardInterrupt:
    client.close_connection(client.client)

