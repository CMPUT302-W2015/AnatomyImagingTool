import bluetooth
import platform
import GlobalVariables

class BluetoothSender():
    def __init__(self):
        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"                
        TV_ADDRESS = "00:1B:DC:0F:2A:E8"
        TABLET_ADDRESS = "AC:22:0B:57:FE:70"

        if GlobalVariables.device == "TV":
            addr = TABLET_ADDRESS
            print("I'm a TV")  
        else:
            addr = TV_ADDRESS
            print("I'm a tablet")
        #search for server

        #search for server
        print("BTS:searching...")

        while True:
            service_matches = bluetooth.find_service( uuid = uuid, address = addr )
            if (len(service_matches) > 0): 
                break

        #setup parameter for outgoing connection
        first_match = service_matches[0]
        self.port = first_match["port"] 
        self.name = first_match["name"]
        self.host = first_match["host"]
        #print("BTS:connecting to \"%s\" on %s..." %(name, host))

        #connect to server
        self.sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        
    def connect(self):
        self.sock.connect((self.host, self.port))
        print("BTS:connected to \"%s\" on %s" %(self.name, self.host))
        
    def send(self, msg):
            self.sock.send(msg)
            
    def disconnect1(self):
            self.sock.send("$close")
            
    def disconnect2(self):
            self.sock.close()
            print("BTS:connection closed")
                    
            