from PyQt4.QtGui import QGridLayout, QLabel, QDialog, QSlider
from PyQt4.QtCore import Qt
import numpy as np

'''
Created on Mar 10, 2015

Edit the opacity of the image.
This can be controlled from the toolbar 
'''

class OpacityEditor(QDialog):
    def __init__(self, volumeProperty, reader, renWin):
        super(OpacityEditor, self).__init__()  
        self.volumeProperty = volumeProperty
        self.reader = reader
        self.renWin = renWin
        self.setWindowTitle("Opacity Editor") 
        self.opacityfunction =  self.volumeProperty.GetScalarOpacity(0)
        self.npts = self.opacityfunction.GetSize()
        
        self.vScale = [[QSlider(Qt.Horizontal) for i in range(4)] for j in range(self.npts)]  
        self.label_value = [[QLabel(" ") for i in range(4)] for j in range(self.npts)]  
        
        label_scaleName = [QLabel() for j in range(4)]
        for j, text in enumerate(("Intensity", "Opacity","Midpoint","Sharpness")):
            label_scaleName[j].setText(text)       
        
        layout = QGridLayout()
        
        for j in range(4):
            layout.addWidget(label_scaleName[j],0,2*j)
        
        rmax = self.reader.GetOutput().GetScalarRange()[1] if self.reader.GetOutput().GetScalarRange()[1]> self.opacityfunction.GetRange()[1] else self.opacityfunction.GetRange()[1]
        rmin = self.reader.GetOutput().GetScalarRange()[0] if self.reader.GetOutput().GetScalarRange()[0] < self.opacityfunction.GetRange()[0] else self.opacityfunction.GetRange()[0]
        opacityNode = np.empty((4,))

        for i in range(self.npts):
            self.opacityfunction.GetNodeValue(i, opacityNode)
            for j in range(4):
                layout.addWidget(self.label_value[i][j],2*i,2*j+1)
                layout.addWidget(self.vScale[i][j],2*i+1,2*j,1,2)  
                if j==0:
                    self.vScale[i][j].setMinimum(rmin)
                    self.vScale[i][j].setMaximum(rmax)
                    self.vScale[i][j].setValue(opacityNode[j])
                else:        
                    self.vScale[i][j].setValue(100*opacityNode[j])

                self.vScale[i][j].valueChanged.connect(self.updateOpacity)
        
        self.updateOpacity()
        
        layout.setSpacing(0)
        layout.setHorizontalSpacing(10)
        self.setLayout(layout)
        self.resize(400,50*self.npts)
        
    def updateOpacity(self):
        self.opacityfunction.RemoveAllPoints()
        for i in range(self.npts):
            self.opacityfunction.AddPoint(self.vScale[i][0].value(),0.01*self.vScale[i][1].value(),0.01*self.vScale[i][2].value(),0.01*self.vScale[i][3].value())

            for j in range(4):
                if j == 0:
                    self.label_value[i][j].setText(str(self.vScale[i][j].value()))
                else:
                    self.label_value[i][j].setText(str(0.01*self.vScale[i][j].value()))
            
        self.volumeProperty.SetScalarOpacity(self.opacityfunction)
        self.renWin.Render()            