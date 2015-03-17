import bluetooth
import sys

class BluetoothSender():
    
    def __init__(self, addr):

        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

        #search for server
        print("searching for device...")

        print (uuid + " / " + addr)
        while True:
            service_matches = bluetooth.find_service( uuid = uuid, address = addr )
            if (len(service_matches) > 0): 
                break
        print("device found")

        #setup parameter for outgoing connection
        first_match = service_matches[0]
        port = first_match["port"] 
        name = first_match["name"]
        host = first_match["host"]
        print("setting up outgoing connection to \%s\" on %s..." %(name, host))

        #connect to server
        self.sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        self.sock.connect((host, port))
        print("outgoing connection established")
        
        def send(self, msg):
            self.sock.send(msg)
            
        def disconnect(self):
            self.sock.close()
            print("outgoing bluetooth connection closed")
            
            