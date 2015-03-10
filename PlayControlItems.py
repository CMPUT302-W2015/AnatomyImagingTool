'''
Created on Mar 10, 2015

@author: Bradley
'''

class PlayControlItems(QWidget):
    def __init__(self, master):
        super(PlayControlItems, self).__init__()
        master.slider_imageNumber = QSlider(Qt.Horizontal)
        master.slider_imageNumber.setPageStep(1)
        master.label_imageNumber = QLabel('')
        master.label_imageNumber.setFixedWidth(80)
        master.button_iterate = QPushButton("Play/Stop")
        layout = QGridLayout() 
        layout.addWidget(master.label_imageNumber,0,0)
        layout.addWidget(master.slider_imageNumber,1,0)
        layout.addWidget(master.button_iterate,1,1)
        layout.setMargin(5)
                            
        for col, val in enumerate((4,1)):
            layout.setColumnStretch(col,val)  
            
        master.slider_imageNumber.setEnabled(False)
        master.button_iterate.setEnabled(False)      
    
        self.setLayout(layout)      