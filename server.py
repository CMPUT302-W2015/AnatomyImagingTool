import sys
from socket import socket, AF_INET, SOCK_DGRAM
from _socket import gethostbyname

SERVER_IP = '10.19.216.65'
PORT_NUMBER = 5000
SIZE = 102

hostName = gethostbyname('0.0.0.0')

socket = socket(AF_INET, SOCK_DGRAM)
socket.bind((hostName, PORT_NUMBER))

while True:
        (data, addr) = socket.recvfrom(SIZE)
        print data

sys.exit()