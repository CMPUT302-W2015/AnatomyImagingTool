from PyQt4.QtGui import QGridLayout, QWidget, QLabel, QPushButton, QComboBox, QSlider, QLineEdit
from PyQt4.QtCore import Qt

'''
Created on Mar 10, 2015

@author: Bradley
'''

class LabelControlItems(QWidget):
    def __init__(self):
        super(LabelControlItems, self).__init__()
        
        nlabels = 5
        
        self.combobox_labels = QComboBox()
        self.label_label = QLabel("Label: ")
        self.label_text = QLabel("Text: ")
        self.text_label = QLineEdit("Label1")
        self.button_label = QPushButton("On/Off")
        
        self.scale_labelsize = QSlider(Qt.Horizontal)
        self.label_labelsize = QLabel("Label Size")
        self.scale_labelsize.setMinimum(1)
        self.scale_labelsize.setValue(20)
        
        self.button_label.setCheckable(True)
        
        for i in range(nlabels):
            self.combobox_labels.addItem("Label"+str(i+1))
            
        layout = QGridLayout()
        
        layout.addWidget(self.label_label,0,0)
        layout.addWidget(self.combobox_labels,1,0)
        layout.addWidget(self.label_text,0,1)
        layout.addWidget(self.text_label,1,1)
        layout.addWidget(self.button_label,1,2)

        layout.addWidget(self.label_labelsize,0,3)
        layout.addWidget(self.scale_labelsize,1,3)        


            
        
            
        for col, stretch in enumerate((5,5,5,5)):
            layout.setColumnStretch(col, stretch)            
        
        layout.setMargin(5)
        layout.setHorizontalSpacing(5)       
        layout.setVerticalSpacing(0)                  
        self.setLayout(layout)