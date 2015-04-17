'''
This module is is the sender for the Bluetooth connection.
It sends the Bluetooth signals to be receieved by the listener. 
Uses threading to separate from incoming Bluetooth messages
'''
import bluetooth
import platform
import GlobalVariables

class BluetoothSender():
    def __init__(self):
        self.uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        # These are hardcoded into the program, will have to change for a new device                
        TV_ADDRESS = "00:1B:DC:0F:2A:E8"
        TABLET_ADDRESS = "AC:22:0B:57:FE:70"

        # Get the device type
        if GlobalVariables.device == "TV":
            self.addr = TABLET_ADDRESS
            print("I'm a TV")  
        else:
            self.addr = TV_ADDRESS
            print("I'm a tablet")
        
    '''
    Searches for a connection until one is found, connects with first match found
    '''
    def connect(self):
        print("BTS:searching...")
        while True:
            service_matches = bluetooth.find_service( uuid = self.uuid, address = self.addr )
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
        self.sock.connect((self.host, self.port))
        print("BTS:connected to \"%s\" on %s" %(self.name, self.host))
    
    # Sends a message to the device that it has been connected
    def send(self, msg):
            self.sock.send(msg)
      
    # Disconnects the threads, this is important, can cause Port Issues      
    def disconnect1(self):
            self.sock.send("$close")
    
    # Disconnects the threads, this is important, can cause Port Issues
    def disconnect2(self):
            self.sock.close()
            print("BTS:connection closed")
                    
            