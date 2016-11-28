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
client_conn_list = []
# list used to store all clients addr
client_addr_list = []

# method used to poll clients to determine if they are online
def test_clients():
    while 1:
        try:
            counter = -1
            for client in client_addr_list:
                counter += 1
                print(str(client))
                test_str = " "
                client_conn_list[counter].send(test_str.encode('utf-8'))
            time.sleep(1)
        except socket.error as msg:
            print("client disconnected")
            client_addr_list.remove(client)
            del client_conn_list[counter]
            print("new client list: " + str(client_addr_list))
            clients_updated()

start_new_thread(test_clients,())


# handle connections, function used to create threads
def client_thread(conn):
    conn.send(welcome_banner.encode('utf-8'))
    # TODO: SEND LIST OF ALL ACTIVE CLIENTS
    port = conn.recv(4096)
    print("CLIENT PORT " + port.decode('utf-8'))

    client_addr_list.append(addr[0] + ":" + port.decode('utf-8'))
    
    clients_updated()


# sends updated client list to all clients
def clients_updated():
    counter = -1
    for client in client_conn_list:
        counter += 1
        try:
            client.send(str(client_addr_list).encode('utf-8'))
        except socket.error as msg:
            print("client " + client.getpeername() + " disconnected")
            client_conn_list.remove(client)
            del client_addr_list[counter]
            print("new client list: " + str(client_addr_list))
            clients_updated()

while 1:
    conn, addr = sock.accept()
    print("connected with " + addr[0] + ":" + str(addr[1]))

    # store new client
    client_conn_list.append(conn)
    print(str(client_conn_list))
    
    # start new thread
    start_new_thread(client_thread, (conn,))
