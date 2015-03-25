import BluetoothSender
import BluetoothListener
import time
import GlobalVariables


BTL = BluetoothListener.BluetoothListener()
BTL.start()
BTS = BluetoothSender.BluetoothSender()

BTS.send("testing1")
time.sleep(5)
BTS.send("testing2")
time.sleep(5)
BTS.disconnect()
BTL.wait() #this is required for proper listener closure

print("Main Thread Closed")