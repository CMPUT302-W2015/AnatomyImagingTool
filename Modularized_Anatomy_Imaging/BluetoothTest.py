import BluetoothSender
import BluetoothListener
import time
import GlobalVariables

TV_ADDRESS = "00:1b:dc:0f:2a:e8"
TABLET_ADDRESS = "ac:22:0b:57:fe:70"
OWNER_ADDRESS = "e4:d5:3d:8c:43:12"

BTL = BluetoothListener.BluetoothListener()
BTL.start()
BTS = BluetoothSender.BluetoothSender(TABLET_ADDRESS)

BTS.send("testing1")
time.sleep(5)
BTS.send("testing2")
BTS.send("$")
BTS.disconnect()