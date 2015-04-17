from PyQt4.QtGui import QGridLayout, QWidget, QScrollBar, QLabel, QPushButton
from PyQt4.QtCore import Qt

'''
Created on Mar 10, 2015

@author: Bradley
'''

class CropControlItems(QWidget):
    def __init__(self, master):
        super(CropControlItems, self).__init__()
        
        nscales = 6
        
        master.scale_xmin, master.scale_xmax, master.scale_ymin, master.scale_ymax, master.scale_zmin, master.scale_zmax = [QScrollBar(Qt.Horizontal) for i in range(nscales)]
        label_xmin, label_xmax, label_ymin, label_ymax, label_zmin, label_zmax = [QLabel() for i in range(nscales)]
        
        master.button_resetcrop = QPushButton("Crop Reset")
        master.button_box = QPushButton("BoxWidget On/Off",)
        layout = QGridLayout()            
        for index, label, labeltext, labelcolor in zip(range(nscales), (label_xmin, label_xmax, label_ymin, label_ymax, label_zmin, label_zmax), ("X min", "X max", "Y min", "Y max", "Z min", "Z max"),\
                                                       ("red", "red", "green", "green", "blue", "blue")):
            label.setText(labeltext)
            label.setStyleSheet("QLabel {color:" + labelcolor +" ; }");
            layout.addWidget(label, 0, index)
            
        layout.addWidget(master.button_box, 0, index + 1)
                    
        for index, scale in enumerate((master.scale_xmin, master.scale_xmax, master.scale_ymin, master.scale_ymax, master.scale_zmin, master.scale_zmax, master.button_resetcrop)):            
            scale.setEnabled(False)
            layout.addWidget(scale, 1, index)

        master.button_box.setEnabled(False)
            
        layout.setMargin(5)
        layout.setHorizontalSpacing(20)       
        layout.setVerticalSpacing(0)     
                    
        self.setLayout(layout)