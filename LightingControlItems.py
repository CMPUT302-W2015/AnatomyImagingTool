'''
Created on Mar 10, 2015

@author: Bradley
'''

class LightingControlItems(QWidget):
    def __init__(self):
        super(LightingControlItems, self).__init__()
        
        self.button_shade = QPushButton('Shade On/Off')
        self.button_interpolation = QPushButton('Interpolation: Linear/NN ')
        self.button_gradientopacity = QPushButton('Gradient Opacity On/Off')

        for comp in (self.button_shade, self.button_interpolation, self.button_gradientopacity):
            comp.setCheckable(True)
        
        self.slider_ambient = QSlider(Qt.Horizontal)    
        self.slider_diffuse = QSlider(Qt.Horizontal)
        self.slider_specular = QSlider(Qt.Horizontal)                
        self.slider_keylightintensity = QSlider(Qt.Horizontal)
        self.slider_ambient.setValue(100.0)
        self.slider_diffuse.setValue(100.0)        
        self.slider_keylightintensity.setValue(20)
              
        for comp in (self.button_shade, self.button_interpolation, self.button_gradientopacity, self.slider_ambient, self.slider_diffuse, self.slider_specular, self.slider_keylightintensity):
            comp.setEnabled(False)
        
        self.label_ambient = QLabel('Ambient: 1.0')
        self.label_diffuse = QLabel('Diffuse: 1.0')
        self.label_specular = QLabel('Specular: 0.0')

        self.label_keylightintensity = QLabel('Key Light Intensity: 4.0')

        layout = QGridLayout() 
        
        for ind, comp in enumerate((self.label_ambient, self.label_diffuse, self.label_specular, self.label_keylightintensity)):
            layout.addWidget(comp,0,ind)
        
        for ind, comp in enumerate((self.slider_ambient, self.slider_diffuse, self.slider_specular, self.slider_keylightintensity)):
            layout.addWidget(comp,1,ind)
        
        layout.addWidget(self.button_interpolation,0,ind+1)
        layout.addWidget(self.button_gradientopacity,1,ind+1)
        layout.addWidget(self.button_shade,1,ind+2)
        
        layout.setMargin(5)
        layout.setVerticalSpacing(0)
                
        self.setLayout(layout) 