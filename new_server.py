from Bluetooth_listener import Bluetooth_listener
from bluetooth import *
import time
import sys
rcv_thread = Bluetooth_listener()
rcv_thread.start()
time.sleep(10)
addr = "ac:22:0b:57:fe:70"
uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
service_matches = find_service( uuid=uuid, address=addr)
if len(service_matches) == 0:
    print("couldn't find the SampleServer service =(")
    sys.exit(0)
first_match = service_matches[0]
port = first_match["port"]
name = first_match["name"]
host = first_match["host"]

print("connecting to \%s\" on %s" %(name, host))


sock = BluetoothSocket( RFCOMM )
sock.connect((host, port))

while True:
    data = raw_input("enter input:")
    if len(data) == 0: break
    sock.send(data)
    
sock.close()
