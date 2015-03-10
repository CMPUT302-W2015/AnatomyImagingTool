import sysconfig    
from socket import socket, AF_INET, SOCK_DGRAM

SERVER_IP = '10.19.216.65'
PORT_NUMBER = 5000
SIZE = 1024

socket = socket(AF_INET, SOCK_DGRAM)
while True:
    socket.sendto('cool', (SERVER_IP, PORT_NUMBER))
exit()