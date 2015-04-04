import bluetooth
import threading
from PyQt4.QtCore import QThread
import GlobalVariables

"""
Note that each instantiation of this class creates a new thread. 
"""
class BluetoothListener(QThread):
    def __init__(self):
        QThread.__init__(self)
        #self.setDaemon()    #This makes it so that the thread auto-closes when
                            #the parent thread closes
    
    def __del__(self):
        self.wait()
    """
    As per the norm, this listener uses 2 sockets. server_sock listens for 
    connection attempts, and when it finds them, creates another socket,
    client_sock, for the actual communication.
    """    
    def run(self):
        server_sock=bluetooth.BluetoothSocket( bluetooth.RFCOMM )
        server_sock.bind(("",bluetooth.PORT_ANY))
        server_sock.listen(1)        
        port = server_sock.getsockname()[1]
        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
        bluetooth.advertise_service (server_sock, "BluetoothListener",
                                     service_id = uuid,
                                     service_classes = [uuid, bluetooth.SERIAL_PORT_CLASS],
                                     profiles = [bluetooth.SERIAL_PORT_PROFILE]
                                     )           
        print("BTL:waiting for connection on RFCOMM channel %d..." % port)
        client_sock, client_info = server_sock.accept()
        client_info
        print("BTL:connected to %s" %client_info[0])
        
        """
        this block will need to be rewritten depending on what we want to do
        with the incoming data. we should probably call different functions
        depending on the data.
        """        
        try:
            while True:
                data = client_sock.recv(1024)
                if len(data) == 0: 
                    break
                if data == "$close":
                    GlobalVariables.BTS.send("$close_ack") 
                    break
                if data == "$close_ack":
                    break
                #instead of printing, this should call functions or change global variables
                print("%s" % data)
        except IOError:
            pass

        client_sock.close()
        server_sock.close()
        print("BTL:connection closed") 
        print("Server Thread Closed")