import bluetooth
import sys

class BluetoothSender():
    
    def __init__(self, addr):

        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

        #search for server
        print("BTS:searching...")

        print (uuid + " / " + addr)
        while True:
            service_matches = bluetooth.find_service( uuid = uuid, address = addr )
            if (len(service_matches) > 0): 
                break

        #setup parameter for outgoing connection
        first_match = service_matches[0]
        port = first_match["port"] 
        name = first_match["name"]
        host = first_match["host"]
        print("BTS:connecting to \"%s\" on %s..." %(name, host))

        #connect to server
        self.sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        self.sock.connect((host, port))
        print("BTS:connection established")
        
    def send(self, msg):
            self.sock.send(msg)
            
    def disconnect(self):
            self.sock.close()
            print("BTS:connection closed")
            
            