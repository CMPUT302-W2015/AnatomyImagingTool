'''
Module to test the bluetooth connection
'''
import BluetoothSender
import BluetoothListener
import time
import GlobalVariables

TV_ADDRESS = "00:1B:DC:0F:2A:E8"
TABLET_ADDRESS = "AC:22:0B:57:FE:70"
OWNER_ADDRESS = "e4:d5:3d:8c:43:12"

BTL = BluetoothListener.BluetoothListener()
BTL.start()
BTS = BluetoothSender.BluetoothSender(TABLET_ADDRESS)

BTS.send("testing1")
time.sleep(5)
BTS.send("testing2")
time.sleep(5)
BTS.disconnect()
BTL.wait() #this is required for proper listener closure

print("Main Thread Closed")