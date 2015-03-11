from bluetooth import *
import sys
from BluetoothListener import BluetoothListener

#bluetooth address of server
addr = "e4:d5:3d:8c:43:12"

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

#search for server
print("searching for device...")

print (uuid + " / " + addr)
service_matches = find_service( uuid = uuid, address = addr )
if (len(service_matches) == 0): 
    print("no device found :(")
    sys.exit(0)
print("device found")

#setup parameter for outgoing connection
first_match = service_matches[0]
port = first_match["port"] 
name = first_match["name"]
host = first_match["host"]
print("setting up outgoing connection to \%s\" on %s..." %(name, host))

#connect to server
sock=BluetoothSocket( RFCOMM )
sock.connect((host, port))
print("outgoing connection established")

#open incoming port on separate thread
rcv_thread = BluetoothListener()
rcv_thread.start()

#
while True:    
    data = raw_input()
    if len(data) == 0: break
    if (data=="quit"):
        rcv_thread.exit()
        sock.close()
        print ("Connection disconnected")
        sys.exit()
    sock.send(data)

sock.close()
print("outgoing connection disconnected")