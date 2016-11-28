import socket, sys, time, re
from _thread import *


ip = str(sys.argv[1])
port = int(sys.argv[2])
buff_size = 1024
client_conn = []
welcome_banner = "welcome to the livesync tracking server!"

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("socket  created")

try:
    sock.bind((ip, port))
except socket.error as msg:
    print("Bind failed. " + str(msg))
    sock.close()
    sys.exit()

print("socket bind complete")

sock.listen(10)
print("socket now listening ")

# list used to store all clients
client_list = []


# handle connections, function used to create threads
def client_thread(conn):
    conn.send(welcome_banner.encode('utf-8'))
    # TODO: SEND LIST OF ALL ACTIVE CLIENTS
    conn.send(str(client_list).encode('utf-8'))


while 1:
    conn, addr = sock.accept()
    print("connected with " + addr[0] + ":" + str(addr[1]))

    # store new client
    client_list.append(conn)
    print(str(client_list))

    # start new thread
    start_new_thread(client_thread, (conn,))
