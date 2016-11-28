import socket, sys, time, re
from _thread import *
import struct

multicast_group = '224.3.29.71'
server_address = ('', 10000)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(server_address)

buff_size = 1024
client_conn = []
welcome_banner = "welcome to the livesync tracking server!"

print("socket bind complete")

# list used to store all clients
client_list = []

group = socket.inet_aton(multicast_group)
mreq = struct.pack('4sL', group, socket.INADDR_ANY)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

# handle connections, function used to create threads
def client_thread(conn):
    conn.send(welcome_banner.encode('utf-8'))
    # TODO: SEND LIST OF ALL ACTIVE CLIENTS
    conn.send(str(client_list).encode('utf-8'))


while 1:
    print("waiting to recv msgs")

    data, address = sock.recvfrom(1024)
    print("recv from " + str(address) + " bytes: " + len(data))
    sock.sendto('ack', address)
