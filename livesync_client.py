import socket, sys, time, re
from _thread import *
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ip and port of client
ip = str(sys.argv[1])
port = int(sys.argv[2])

try:
    # create an AF_INET, STREAM socket (TCP) for tracker
    tracker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
    print('Failed to create tracker socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
    sys.exit()

print('Socket Created')

# Connect to remote server
tracker_sock.connect(('10.100.42.221', 3321))

print('Socket Connected to TRACKER SERVER port ' + str(3321) + ' on ip ' + '10.100.45.57')


def receive_data(tracker_sock):
    while 1:
        # Now receive data
        global live_clients
        reply = tracker_sock.recv(4096)
        if reply.decode('utf-8').startswith('['):
            live_clients = eval(reply.decode('utf-8'))
        print("FROM TRACKER SERVER " + reply.decode())
        tracker_sock.send(str(port).encode('utf-8'))

start_new_thread(receive_data, (tracker_sock,))

print('------')

try:
    # create an AF_INET, STREAM socket (TCP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
    print('Failed to create server socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
    sys.exit()

print('Server socket created')



buff_size = 1024
client_conn = []

try:
    sock.bind((ip, port))
except socket.error as msg:
    print("Bind failed. " + str(msg))
    sock.close()
    sys.exit()

print("server socket bind complete")

sock.listen(10)
print("This client is now listening ")

print('------')

welcome_banner = "You have connected to " + ip + " on port " + str(port)


def send_to_client(client_ip, client_port):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print('Failed to create client socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
        sys.exit()

    client_socket.connect((client_ip, int(client_port)))

    client_msg = "hello!"
    client_socket.send(client_msg.encode('utf-8'))

    client_socket.close()


class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print("Got it!")
        local_name = sock.getsockname();
        print(local_name)
        print(live_clients)
        for client in live_clients:
            match = re.search("(.*):(.*)", client)
            if match:
                # print("MATCH " + match.group(1) + " " + match.group(2))
                if match.group(1) != local_name[0] or match.group(2) != str(local_name[1]):
                    print("START NEW THREAD")
                    start_new_thread(send_to_client, (match.group(1), match.group(2)))

event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path='.', recursive=False)
observer.start()
#
# try:
#     while True:
#         time.sleep(1)
# except KeyboardInterrupt:
#     observer.stop()
# observer.join()


# handle connections, function used to create threads
def client_thread(connection):
    try:
        conn.send(welcome_banner.encode('utf-8'))
        # TODO: SEND LIST OF ALL ACTIVE CLIENTS
        client_reply = connection.recv(4096)
        print("FROM A CLIENT SERVER " + client_reply.decode('utf-8'))
    except BrokenPipeError:
        exit_thread()

while 1:
    conn, addr = sock.accept()
    print("connected with " + addr[0] + ":" + str(addr[1]))

    # start new thread
    start_new_thread(client_thread, (conn,))



