from PyQt4.QtGui import QGridLayout, QWidget, QScrollBar, QLabel, QPushButton, QDial
from PyQt4.QtCore import Qt, QSize

'''
Created on Mar 10, 2015

@author: Bradley
'''

class PositionControlItems(QWidget):
    def __init__(self, master):
        self.master = master        
        super(PositionControlItems, self).__init__()

        nscales = 4
        master.scale_azimuth, master.scale_elevation, master.scale_roll = [QDial() for i in range(nscales-1)]
        master.scale_stereodepth = QScrollBar(Qt.Horizontal)
        label_azimuth, label_elevation, label_roll, label_stereodepth = [QLabel() for i in range(nscales)]
        master.button_zoomin, master.button_zoomout, master.button_resetcamera = [QPushButton() for i in range(3)]
        label_stereodepth = QLabel("Stereo depth")
        
        for button, buttontext in zip((master.button_zoomin, master.button_zoomout, master.button_resetcamera),("Zoom In", "Zoom Out", "Reset")):
            button.setText(buttontext)
        
        layout = QGridLayout()
        for index, label, labeltext in zip(range(nscales), (label_azimuth, label_elevation, label_roll), ("Azimuth", "Elevation", "Roll")):
            label.setText(labeltext)
            label.setAlignment(Qt.AlignRight)
        
        layout.addWidget(master.button_zoomin, 0, 7)
        layout.addWidget(master.button_zoomout, 0, 8)
        
        for index, scale in enumerate((master.scale_azimuth, master.scale_elevation, master.scale_roll)):
            scale.setMinimum(-179)
            scale.setMaximum(180)
            scale.setValue(0)
            scale.setMaximumSize(QSize(60,60))
            
        for index, comp in enumerate((label_azimuth, master.scale_azimuth,label_elevation,  master.scale_elevation, label_roll, master.scale_roll)):
            layout.addWidget(comp,0,index, 2, 1)
        
        layout.addWidget(master.button_resetcamera, 1, 8)
            
        master.scale_stereodepth.setValue(20)            
        master.scale_stereodepth.setMinimum(10)
        master.scale_stereodepth.setMaximum(100)
        layout.addWidget(label_stereodepth,0,6)            
        layout.addWidget(master.scale_stereodepth,1,6)
        
        layout.setMargin(0)
        layout.setHorizontalSpacing(20)       
        layout.setVerticalSpacing(0)     
        
        for col, val in enumerate((1,2,1,2,1,2,4,4,4)):
            layout.setColumnStretch(col,val)
                    
        self.setLayout(layout)