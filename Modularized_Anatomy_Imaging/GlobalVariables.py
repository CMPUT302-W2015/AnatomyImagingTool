#Global variables for everything related to AnatomyImagingSetup

'''
Created on March 10th, 2015

@author: Bradley
'''
def init():
    import numpy as np
    import BluetoothSender
    import BluetoothListener
    
    global BTS
    global BTL
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
    
    BTS = BluetoothSender.BluetoothSender()
    BTL = BluetoothListener.BluetoothListener()
    BTL.start()
    
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
    
    
    