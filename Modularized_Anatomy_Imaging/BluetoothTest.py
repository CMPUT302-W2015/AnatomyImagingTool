import BluetoothSender
import BluetoothListener
import time

BTL = BluetoothListener.BluetoothListener()
BTS = BluetoothSender.BluetoothSender(address)

while True:
    time.sleep(5)
    BTS.send("testing...")