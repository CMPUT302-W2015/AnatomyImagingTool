from PyQt4.QtGui import QWidget, QPushButton, QHBoxLayout
from PyQt4.QtCore import Qt
'''
Created on Apr 4, 2015

This module adds buttons the Tablet Control tab on the toolbar
Adds the 'Connect Bluetooth', 'Tracking On/Off', and 'Rotate/Stop' buttons.

@author: ANATOMY-IMAGING
'''

class TabletControlItems(QWidget):
    def __init__(self, master):
        self.master = master
        super(TabletControlItems, self).__init__()
        
        nbuttons = 3
        
        master.button_bluetoothConnect, master.button_tracking, master.button_rotateImage = [QPushButton() for i in range(nbuttons)]                    
        buttontext = ["Connect Bluetooth", "Tracking On/Off",  "Rotate/Stop"]
        
        master.button_cameratext.setCheckable(True)
        
        layout = QHBoxLayout() 
        layout.setSpacing(0)
        for index, button in enumerate((master.button_bluetoothConnect, master.button_tracking,  master.button_rotateImage )):
            button.setText(buttontext[index])
            
        for comp in ((master.button_bluetoothConnect, master.button_tracking, master.button_rotateImage )):
            layout.addWidget(comp)
            
        self.setLayout(layout)