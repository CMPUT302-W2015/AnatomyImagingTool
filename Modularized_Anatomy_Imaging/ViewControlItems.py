from PyQt4.QtGui import QGridLayout, QWidget, QLabel, QPushButton

'''
Created on Mar 10, 2015

@author: Bradley
'''

class ViewControlItems(QWidget):
    def __init__(self, master):
        super(ViewControlItems, self).__init__()
        
        nbuttons = 10
        master.button_view = [QPushButton() for i in range(nbuttons)]
        
        self.label_view = QLabel("View")
        self.label_roll = QLabel("Roll")
        
        buttontext = ["XY", "YZ", "ZX", "-XY", "-YZ", "-ZX", "0", "90", "180", "270"]
 
        layout = QGridLayout()
        
        for index in range(nbuttons):
            master.button_view[index].setText(buttontext[index])
            master.button_view[index].setObjectName('button_view%d' % index)
            layout.addWidget(master.button_view[index], 1, index)

        layout.addWidget(self.label_view,0,0)
        layout.addWidget(self.label_roll,0,6)
        
        layout.setMargin(5)
        layout.setHorizontalSpacing(5)       
        layout.setVerticalSpacing(0)                  
        self.setLayout(layout)
