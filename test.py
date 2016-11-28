
MYPORT = 8123
MYGROUP_4 = '225.0.0.250'
MYTTL = 13 # Increase to reach other networks

import time
import struct
import socket
import sys

addrinfo = socket.getaddrinfo(MYGROUP_4, None)[0]

s = socket.socket(addrinfo[0], socket.SOCK_DGRAM)

# Set Time-to-live (optional)
ttl_bin = struct.pack('@i', MYTTL)
if addrinfo[0] == socket.AF_INET:  # IPv4
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl_bin)
else:
    s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_MULTICAST_HOPS, ttl_bin)

while True:
    data = repr(time.time())
    s.sendto(data.encode('utf-8'), (addrinfo[4][0], MYPORT))
    time.sleep(1)
