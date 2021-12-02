from protocol import *
from os import walk

def chooseFile():
    files = []
    for root, dirs, file in walk('files/'):
        for filename in file:
            files.append(filename)
    
    i = 0
    print('choose the file to send to server:')
    for file in files:
        print(str(i) + '. ' + str(file))
        i += 1
    
    x = int(input())
    while x >= i:
        print('not a choice')
        x = int(input())
    
    return files[x], files[x].split('.')[1]

try:
    client = udp_connection()
    client.open_socket('localhost', 5000, 'client')

    filename, extension = chooseFile()

    msg = extension
    client.rdt_send(msg.encode())

    client.send_file('files/' + filename)

    msg, address = client.rdt_recv()
    dicio = eval(msg.decode())
    filename = 'sendByServer_' + dicio['data'].decode() + '.' + extension

    client.recv_file(filename)

    client.close_connection()

except KeyboardInterrupt:
    client.close_connection()

