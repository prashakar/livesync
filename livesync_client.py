import socket, sys, time, re, os, random
from _thread import *
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import urllib.request

# ip and port of client
#ip = str(sys.argv[1])
#port = int(sys.argv[2])

# get ip of this client
#ip = str(socket.gethostbyname(socket.gethostname()))
#print("Your Client IP: " + ip)

#if (ip == "127.0.0.1" or ip == "127.0.1.1"):
#    print('IP is not valid, finding IP')
ip = str(input("Enter this PC's IP:\n"))
print("Your client IP\n" + ip)

# randomly generate unassigned port number
port = int(random.randint(49152, 65535))

try:
    # create an AF_INET, STREAM socket (TCP) for tracker
    tracker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
    print('Failed to create tracker socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
    sys.exit()

print('Socket Created')

#server_ip = input("Enter server IP:\n")
#server_port = input("Enter server PORT:\n")

server_ip = '52.34.233.122'
server_port = '49445'

# Connect to remote server
tracker_sock.connect((str(server_ip), int(server_port)))

print('Socket Connected to TRACKER SERVER port ' + str(server_port) + ' on ip ' + str(server_ip))


def receive_data(tracker_sock):
    """
    Receives client list data from tracking server.
    Send this clients port number to tracking server.
    
    Keyword arguments:
    tracker_sock -- tracking server socket object
    """
    while 1:
        # stores list of all clients
        global live_clients
        reply = tracker_sock.recv(4096)
        # reply is a client list
        if reply.decode('utf-8').startswith('['):
            live_clients = eval(reply.decode('utf-8'))
        print("FROM TRACKER SERVER " + reply.decode())

        # send this clients port number
        tracker_sock.send(str(port).encode('utf-8'))


start_new_thread(receive_data, (tracker_sock,))

print('------------')

try:
    # create an AF_INET, STREAM socket (TCP)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as msg:
    print('Failed to create server socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
    sys.exit()

print('Server socket created')

buff_size = 8192
client_conn = []

try:
    # bind this clients ip and randomly generated port
    sock.bind((ip, port))
except socket.error as msg:
    print("Bind failed. " + str(msg))
    sock.close()
    sys.exit()

print("server socket bind complete")

sock.listen(10)
print("This client is now listening ")

print('------------')

welcome_banner = "You have connected to " + ip + " on port " + str(port)

class CompleteResponseThread(threading.Thread):
    def __init__(self, client_socket):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
    def run(self):
        while 1:
            client_response = self.client_socket.recv(1024)
            if (client_response.decode('utf-8') == "DONE RECEIVING DATA"):
                print("FROM REMOTE CLIENT: " + client_response.decode('utf-8'))
                break


def send_to_client(client_ip, client_port, file):
    """
    Sends data to remote client.

    Keyword arguments:
    client_ip -- ip of the remote client
    client_port -- port of the remote client
    file -- absolute file path of modified file on this local client
    """
    try:
        # create new socket to connect to remote client
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error as msg:
        print('Failed to create client socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1])
        sys.exit()

    try:
        # connect to remote client
        client_socket.connect((client_ip, int(client_port)))
    except TimeoutError:
        print("socket timed out")

    # generate filename string to send as first msg
    send_str = "NAME:" + file[14:] + ";"
    print("Sending filename... " + send_str)
    # send name of the file modified
    client_socket.send(send_str.encode('utf-8'))

    # open the modified file to send byte data
    f = open(file, 'rb')

    print('Sending file...')
    l = f.read(buff_size)
    while l:
        print('Sending...')
        client_socket.send(l)
        l = f.read(buff_size)
    print("DONE SENDING!")
    client_socket.shutdown(1)
    # wait until confirmation is received that all data is received
    listen_thread = CompleteResponseThread(client_socket)
    listen_thread.start()
    
    while (listen_thread.isAlive()):
        time.sleep(1)
   
    client_socket.close()
    exit_thread()
    return

class MyHandler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print("Received created event - %s" % event.src_path)

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print("Received modified event - %s" % event.src_path)
            # directory of absolute modified file path
            file = str(event.src_path)
            # filter out swp files
            if "swp" not in file:
                # store this clients ip and port num
                local_name_raw = urllib.request.urlopen('http://ip.42.pl/raw').read()
                local_name = local_name_raw.decode('utf-8')
                local_port_raw = sock.getsockname()
                local_port = str(local_port_raw[1])
                print(local_name + local_port)

                print(live_clients)
                # iterate for every client in the live client list from tracking server
                for client in live_clients:
                    # match the ip and port of each live client
                    match = re.search("(.*):(.*)", client)
                    if match:
                        #print("MATCH " + match.group(1) + " " + match.group(2))
                        # only proceed for every client other than this client
                        if match.group(1) != local_name or match.group(2) != local_port:
                            print("START NEW THREAD " + match.group(1) + match.group(2))
                            # start new thread to send data to a remote client
                            start_new_thread(send_to_client, (match.group(1), match.group(2), file))
            else:
                print("SWAP FILE CHANGE DROPPED")


# observer used to monitor filesystem
event_handler = MyHandler()
observer = Observer()
observer.schedule(event_handler, path='./livesync_send', recursive=False)
observer.start()


# handle connections, function used to create threads
def client_thread(connection):
    """
    Retrieves data from remote clients.
    Writes the retrieved file byte data to this local client.

    Keywork Arguments:
    connection -- remote client socket object
    """
    try:
        # store received data from remote client
        client_reply = connection.recv(buff_size)
        # check if the name of the file has been received
        done_name = False
        
        # done receiving response
        completed_message = "DONE RECEIVING DATA"

        while client_reply:
            print("receiving...")
            # filename has not yet been received
            if done_name is False:
                if client_reply.decode('utf-8').startswith('NAME'):
                    done_name = True
                    # client_split[0] contains the name of the file
                    # client_split[1] contains all bytes that are not the filename
                    client_split = client_reply.decode('utf-8')[6:].split(';')
                    print("found name " + client_split[0])
                    # initially write to filesystem based on the filename received
                    f = open('./livesync_received/' + client_split[0], 'wb')
                    # write any additional bytes
                    f.write(str.encode(client_split[1]))
                    # check for more data from remote client
                    client_reply = connection.recv(buff_size)
            else:
                # filename has been received, now all data received is true data
                f.write(client_reply)
                # check for more data from remote client
                client_reply = connection.recv(buff_size)

        print("All data received successfully from remote client") 
        # done receiving data
        connection.send(completed_message.encode('utf-8'))
        connection.close()
        return
    except BrokenPipeError:
        print("ERRRRRRRRRORRR")
        exit_thread()

# accept connections to this client on main thread
while 1:
    conn, addr = sock.accept()
    print("connected with " + addr[0] + ":" + str(addr[1]))

    # start new thread to receive data from remote client everytime new connection is accepted
    start_new_thread(client_thread, (conn,))
