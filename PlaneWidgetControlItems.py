'''
Created on Mar 10, 2015

@author: Bradley
'''

class PlaneWidgetControlItems(QWidget):
    def __init__(self):
        super(PlaneWidgetControlItems, self).__init__()
        
        nwidgets = 6
        
        self.button_pwidgets = [QPushButton() for i in range(nwidgets)]
        self.button_pwidgetreset = [QPushButton() for i in range(nwidgets)]
        self.button_pwdigetresetall = QPushButton("Reset All")
        self.button_pwdigetresetall.setEnabled(False)
        layout = QGridLayout()  
        for i in range(nwidgets):
            self.button_pwidgets[i].setText("Plane Widget - " + str(i+1))
            self.button_pwidgets[i].setCheckable(True)
            self.button_pwidgets[i].setEnabled(False)
            layout.addWidget(self.button_pwidgets[i],0,i)
            
            self.button_pwidgetreset[i].setText("Reset - " + str(i+1))
            self.button_pwidgetreset[i].setObjectName('resetplane%d' % i)
            self.button_pwidgetreset[i].setEnabled(False)
            layout.addWidget(self.button_pwidgetreset[i],1,i)
        
        layout.addWidget(self.button_pwdigetresetall,1,i+1)
            
        layout.setMargin(5)
        layout.setVerticalSpacing(0)
                    
        self.setLayout(layout)          