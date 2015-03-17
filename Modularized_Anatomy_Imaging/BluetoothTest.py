import BluetoothSender
import BluetoothListener
import time

TV_ADDRESS = "00:1b:dc:0f:2a:e8"
TABLET_ADDRESS = "ac:22:0b:57:fe:70"

BTL = BluetoothListener.BluetoothListener()
BTL.start()
BTS = BluetoothSender.BluetoothSender(TABLET_ADDRESS)

while True:
    time.sleep(5)
    BTS.send("testing...")