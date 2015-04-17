from PyQt4.QtGui import QGridLayout, QWidget, QLabel, QPushButton, QSlider
from PyQt4.QtCore import Qt

'''
Created on Mar 10, 2015

Controller for the smoothing controls on the toolbar
'''

class SmoothingControlItems(QWidget):
    def __init__(self, master):
        super(SmoothingControlItems, self).__init__()    
        
        master.button_nosmooth = QPushButton('No Smoothing')
        master.button_lowsmooth = QPushButton('Low Smoothing')
        master.button_midsmooth = QPushButton('Medium Smoothing')
        master.button_highsmooth = QPushButton('High Smoothing')
        
        master.slider_xsmooth = QSlider(Qt.Horizontal)    
        master.slider_ysmooth = QSlider(Qt.Horizontal)
        master.slider_zsmooth = QSlider(Qt.Horizontal)
        
        master.label_xsmooth = QLabel('')
        master.label_ysmooth = QLabel('')
        master.label_zsmooth = QLabel('')

        layout = QGridLayout() 
        
        for index, button in enumerate((master.button_nosmooth, master.button_lowsmooth, master.button_midsmooth, master.button_highsmooth)):
            layout.addWidget(button, 1, index)
        
        layout.addWidget(master.label_xsmooth,0,index+1)
        layout.addWidget(master.label_ysmooth,0,index+2)
        layout.addWidget(master.label_zsmooth,0,index+3)
        
        layout.addWidget(master.slider_xsmooth,1,index+1)
        layout.addWidget(master.slider_ysmooth,1,index+2)
        layout.addWidget(master.slider_zsmooth,1,index+3)
        
        
        layout.setMargin(5)
        
        self.setLayout(layout) 