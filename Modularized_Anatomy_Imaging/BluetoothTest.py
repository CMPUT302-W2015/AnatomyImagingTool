import BluetoothSender
import BluetoothListener
import time

BTL = BluetoothListener.BluetoothListener()
BTL.start()
BTS = BluetoothSender.BluetoothSender("ac:22:0b:57:fe:70")

while True:
    time.sleep(5)
    BTS.send("testing...")