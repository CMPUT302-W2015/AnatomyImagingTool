from BluetoothListener import BluetoothListener
from bluetooth import *
import time
import sys

#bluetooth address of client
addr = "ac:22:0b:57:fe:70"
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

#open incoming port on separate thread
rcv_thread = BluetoothListener()
rcv_thread.start()

#search for client
print("searching for device...")
while True:    
    service_matches = find_service( uuid=uuid, address=addr)
    if len(service_matches) > 0: break
print("device found")  

#setup parameters for outgoing connection     
first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]
print("setting up outgoing connection to \%s\" on %s..." %(name, host))

#connect to client
sock = BluetoothSocket( RFCOMM )
sock.connect((host, port))
print("outgoing connection established")

#after this point data can be sent freely
while True:
    data = raw_input()
    if len(data) == 0: break
    sock.send(data)
    
sock.close()
print("outgoing connection disconnected")