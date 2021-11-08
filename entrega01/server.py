from protocol import *

server = udp_connection()
server.open_server(5000)
server.server_connection()