# s224112724 Mischka Strydom & s223084654 Sarah Jessiman

import socket
import selectors
import types
import datetime

TCP_IP = '127.0.0.1' # local host
TCP_PORT = 1243 # port
IoT_devices = list()

# Initialize the number of staff and log
staff_count = 0
log = []

def process_message(client_message):
    global staff_count

    if client_message.startswith("AccessControl"):
        if client_message.endswith("Enters Door"):
            staff_count += 1
            log.append((datetime.datetime.now(), "Staff member entered door", staff_count))
        elif client_message.endswith("Exits Door"):
            staff_count -= 1
            log.append((datetime.datetime.now(), "Staff member exited door", staff_count))
    elif client_message == "EmergencyExitDoorOpen":
        staff_count = 0
        log.append((datetime.datetime.now(), "Emergency exit opened", staff_count))

# formats and prints the log entries
def log_event(event):
    date_time, description, count = event
    log_entry = f"{date_time}, {description}, {count}"
    print(log_entry)

class TCPServer:
    def __init__(self, host, port, name="No device name"):
        self.name = name
        self.host = host
        self.port = port
        self.value = ""

    def check_match(self, host, port):
        if self.host == host and self.port == port:
            return True
        else:
            return False

    def _str_(self):
        return "{0} - {1}:{2} State: {3}".format(self.name, self.host, self.port, self.value)

# function that accepts new connections from IoT devices and register with selectors objs
def accept_wrapper(sock):
    conn, addr = sock.accept()  #
    print("A new device has linked to the server.")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr)
    events = selectors.EVENT_READ
    sel.register(conn, events, data=data)
    IoT_devices.append(TCPServer(addr[0], addr[1]))

# function that handles the data received from the IoT
def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    host = data.addr[0]
    port = data.addr[1]
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data: # updates the device value and name according to data received
            print(recv_data)
            if repr(recv_data)[2] =="1":
                #print(repr(recv_data)[2:])
                IoT_devices[find_device(host, port)].name = repr(recv_data)[4:-1]
            else:
                IoT_devices[find_device(host, port)].value =repr(recv_data)[2:-1]
        else: # in the event of a disconnection
            print("A device has been de-linked.")
            del IoT_devices[find_device(host, port)]
            sel.unregister(sock)
            sock.close()

# function that searches for the devices on the list of IoT devices
def find_device(host, port): # searches based on host and port
    for i in range(0, len(IoT_devices)):
        if IoT_devices[i].check_match(host, port):
            return i
    return -1

# TCP server socket is created
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# host address and port is bound to the socket
server_socket.bind((TCP_IP, TCP_PORT))

# listens for connections coming in
server_socket.listen(1)
print("TCP Server started.")

# create selectors object
sel = selectors.DefaultSelector()
serv_sock = server_socket

serv_sock.setblocking(False)
sel.register(serv_sock, selectors.EVENT_READ, data=None)

while True:

    events = sel.select(timeout=None)

    for key, mask in events:

        if key.data is None:
            accept_wrapper(key.fileobj)
        else:
            service_connection(key, mask)

    for current in IoT_devices:
        print(current)
    print("-" * 60)

