from PyQt4.QtGui import QGridLayout, QLabel, QDialog, QSlider
from PyQt4.QtCore import Qt
import numpy as np

'''
Created on Mar 10, 2015

@author: Bradley
'''

class ColorEditor(QDialog):        
    def __init__(self, volumeProperty, reader, renWin):
        super(ColorEditor, self).__init__()  
        self.volumeProperty = volumeProperty
        self.reader = reader
        self.renWin = renWin
        self.setWindowTitle("Color Editor") 
        
        self.colorfunction =  self.volumeProperty.GetRGBTransferFunction(0)
        self.npts = self.colorfunction.GetSize() 
        
        self.vScale = [[QSlider(Qt.Horizontal) for i in range(6)] for j in range(self.npts)]  
        self.label_value = [[QLabel(" ") for i in range(6)] for j in range(self.npts)]  
        
        label_scaleName = [QLabel() for j in range(6)]
        for j, text in enumerate(("Intensity", "Red","Green","Blue","Midpoint","Sharpness")):
            label_scaleName[j].setText(text)       
        
        layout = QGridLayout()
        
        for j in range(6):
            layout.addWidget(label_scaleName[j],0,2*j)
        
        rmax = self.reader.GetOutput().GetScalarRange()[1] if self.reader.GetOutput().GetScalarRange()[1]> self.colorfunction.GetRange()[1] else self.colorfunction.GetRange()[1]
        rmin = self.reader.GetOutput().GetScalarRange()[0] if self.reader.GetOutput().GetScalarRange()[0] < self.colorfunction.GetRange()[0] else self.colorfunction.GetRange()[0]
        opacityNode = np.empty((6,))

        for i in range(self.npts):
            self.colorfunction.GetNodeValue(i, opacityNode)
            for j in range(6):
                layout.addWidget(self.label_value[i][j],2*i,2*j+1)
                layout.addWidget(self.vScale[i][j],2*i+1,2*j,1,2)  
                if j==0:
                    self.vScale[i][j].setMinimum(rmin)
                    self.vScale[i][j].setMaximum(rmax)
                    self.vScale[i][j].setValue(opacityNode[j])
                else:        
                    self.vScale[i][j].setValue(100*opacityNode[j])

                self.vScale[i][j].valueChanged.connect(self.updateColor)
        
        self.updateColor()
        
        layout.setSpacing(0)
        layout.setHorizontalSpacing(10)
        self.setLayout(layout)
        self.resize(600,50*self.npts)
        
    def updateColor(self):
        self.colorfunction.RemoveAllPoints()
        for i in range(self.npts):
            self.colorfunction.AddRGBPoint(self.vScale[i][0].value(),0.01*self.vScale[i][1].value(),0.01*self.vScale[i][2].value(),0.01*self.vScale[i][3].value(),0.01*self.vScale[i][4].value(),0.01*self.vScale[i][5].value())

            for j in range(6):
                if j == 0:
                    self.label_value[i][j].setText(str(self.vScale[i][j].value()))
                else:
                    self.label_value[i][j].setText(str(0.01*self.vScale[i][j].value()))
            
        self.volumeProperty.SetColor(self.colorfunction)
        self.renWin.Render()       