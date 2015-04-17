#Global variables for everything related to AnatomyImagingSetup

'''
Created on March 10th, 2015

Our way of implementing Global Variables accross modules.
To access variables across modules, GlobalVariables must be imported in the module.
Then use 'GlobalVariables.--variablename---
Add the variables here
'''
def init():
    import numpy as np
    import Architecture
    import BluetoothSender
    import BluetoothListener
    
    global device
    global BTL
    global BTS
    global online
    global bluetoothPaused

    global isprojector
    global initfdir 
    global initddir
    global tfuncdir
    global settings_dir
    global screenshot_dir
    global camMatrix
    global camMat4x4
    
    global imageXDist
    global imageYDist
    global imageZDist
    
    
    device = Architecture.get()
    online = False #this is used by the handler for the close button also
    BTL = BluetoothListener.BluetoothListener()
    BTS = BluetoothSender.BluetoothSender()
    
    isprojector = False
    initfdir = ''
    initddir = ''
    tfuncdir = '../Presets\\TransferFunctions\\'
    settings_dir = 'settings'
    screenshot_dir = 'screenshots'
    
    camMatrix = np.array([1.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.541127, -0.840941, 0.000000, 0.000000, 0.840941, 0.541127, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000])
    camMat4x4 = np.reshape(camMatrix, (4,4))
    
    #Represents dimensions of imported image
    imageXDist = 0
    imageYDist = 0
    imageZDist = 0
    
    #BTS = BluetoothSender.BluetoothSender()
    
    
# def bluetoothConnect():
#     import BluetoothSender
#     import BluetoothListener
# 
#     online = True #this is used by the handler for the close button also
#     if online == True:
#         BTL = BluetoothListener.BluetoothListener()
#         BTL.start()
#         BTS = BluetoothSender.BluetoothSender()

        
    
    
    