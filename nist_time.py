'''
Implementation des RFC 868 mit der Nutzung von UDP

RFC 868                                                         May 1983
Time Protocol
When used via UDP the time service works as follows:

   S: Listen on port 37 (45 octal).
   U: Send an empty datagram to port 37.
   S: Receive the empty datagram.
   S: Send a datagram containing the time as a 32 bit binary number.
   U: Receive the time datagram.

   The server listens for a datagram on port 37.  When a datagram
   arrives, the server returns a datagram containing the 32-bit time
   value.  If the server is unable to determine the time at its site, it
   should discard the arriving datagram and make no reply.

The Time
The time is the number of seconds since 00:00 (midnight) 1 January 1900
GMT, such that the time 1 is 12:00:01 am on 1 January 1900 GMT; this
base will serve until the year 2036.
For example:

   the time  2,208,988,800 corresponds to 00:00  1 Jan 1970 GMT,
             2,398,291,200 corresponds to 00:00  1 Jan 1976 GMT,
             2,524,521,600 corresponds to 00:00  1 Jan 1980 GMT,
             2,629,584,000 corresponds to 00:00  1 May 1983 GMT,
        and -1,297,728,000 corresponds to 00:00 17 Nov 1858 GMT.

'''


import socket
import sys
from datetime import datetime

# 70 Jahre in Sekunden
TIME1970 = 2208988800
HOST = sys.argv[1]
PORT = 37

server_address = (HOST, PORT)

# UDP Socket: AF_INET -> IPv4, SOCK_DGRAM -> UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)



try:
    sock.send(b"")
    data = sock.recv(4)
    if len(data) != 4:
        raise ValueError("Invalid response length")

    timestamp = int.from_bytes(data, 'big')
    dt = datetime.fromtimestamp(timestamp  - TIME1970)

    print(dt)

finally:
    sock.close()
