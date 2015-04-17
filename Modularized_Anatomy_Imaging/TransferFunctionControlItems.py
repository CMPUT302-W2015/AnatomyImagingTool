from PyQt4.QtGui import QWidget, QLabel, QPushButton, QHBoxLayout, QComboBox
from PyQt4.QtCore import Qt

'''
Created on Mar 10, 2015

@author: Bradley
'''

class TransferFunctionControlItems(QWidget):
    def __init__(self, master):
        super(TransferFunctionControlItems, self).__init__()
        self.button_edittransfunction, self.button_editopacity, self.button_editcolor, self.button_editgradient, self.button_savetfunction = [QPushButton() for i in range(5)]
        buttontext = ["Edit Transfer Function", "Edit Opacity", "Edit Color", "Edit Gradient Opacity", "Save Transfer Function"]        
     
        self.combobox_transfunction = QComboBox()
        label_transfunction = QLabel("Transfer Function")
        label_transfunction.setAlignment(Qt.AlignCenter)
     
        for index, button in enumerate((self.button_edittransfunction, self.button_editopacity, self.button_editcolor, self.button_editgradient, self.button_savetfunction)):
            button.setText(buttontext[index])
     
        layout = QHBoxLayout() 
        layout.setSpacing(0)
        for comp in ((label_transfunction, self.combobox_transfunction, self.button_edittransfunction, self.button_editopacity, self.button_editcolor, self.button_editgradient, self.button_savetfunction)):
            layout.addWidget(comp)
     
        self.setLayout(layout)