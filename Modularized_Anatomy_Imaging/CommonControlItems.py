from PyQt4.QtGui import QWidget, QPushButton, QHBoxLayout

'''
Created on Mar 10, 2015

Creates the buttons for the main screen of the control bar
Also calls the appropriate functions when button pressed.
'''

class CommonControlItems(QWidget):
    def __init__(self, master):
        self.master = master
        super(CommonControlItems, self).__init__()
        
        nbuttons = 8
        
        # Names of the buttons
        master.button_loadEcho, master.button_loadDir, master.button_rotate, \
            master.button_stereo, master.button_measurement, master.button_anglemeasurement,  master.button_cameratext, master.button_savescreen = [QPushButton() for i in range(nbuttons)]                    
        buttontext = ["Load Echo", "Load MR/CT",  "Rotate/Stop", "Stereo On/Off", "Distance Meas. On/Off", "Angle Meas. On/Off", "Display Orientation", "Save Screen"]
               
        master.button_cameratext.setCheckable(True)
        
        layout = QHBoxLayout() 
        layout.setSpacing(0)
        for index, button in enumerate((master.button_loadEcho, master.button_loadDir,  master.button_rotate, \
            master.button_stereo, master.button_measurement, master.button_anglemeasurement, master.button_cameratext, master.button_savescreen )):
            button.setText(buttontext[index])
            
        for comp in ((master.button_loadEcho, master.button_loadDir, master.button_rotate,  \
            master.button_stereo, master.button_measurement, master.button_anglemeasurement, master.button_cameratext, master.button_savescreen )):
            layout.addWidget(comp)
            
        self.setLayout(layout)