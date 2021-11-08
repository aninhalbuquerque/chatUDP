from protocol import *

client = udp_connection()
client.open_client('localhost', 5000)
client.client_connection()