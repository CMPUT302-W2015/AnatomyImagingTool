from PyQt4.QtGui import QApplication, QMainWindow, QFrame, QGridLayout, QWidget, QScrollBar, QLabel, QTabWidget, QPushButton, QHBoxLayout, QSpinBox, QFileDialog, QComboBox, QGroupBox, QVBoxLayout, QDial, QDialog, QSlider, QMenu, QLineEdit
from PyQt4.QtCore import Qt, QFile, QLatin1String, QSize
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk, sys, dicom, numpy as np, glob, xml.etree.ElementTree as ET, os, datetime, colorsys
from ui.widgets.transferfunction import TransferFunction, TransferFunctionWidget
from PySide.QtGui import QDialog as pysideQWidget
from PySide.QtGui import QGridLayout as pysideQGridLayout
import vrpn
import math

isprojector = False

initfdir = ''
initddir = ''
tfuncdir = 'Presets\\TransferFunctions\\'
settings_dir = 'settings'
screenshot_dir = 'screenshots'

camMatrix = np.array([1.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.541127, -0.840941, 0.000000, 0.000000, 0.840941, 0.541127, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000])
camMat4x4 = np.reshape(camMatrix, (4,4))


class TDViz(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        
        self.frame = QFrame()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        
        self.cropControlItems = CropControlItems(self)
        self.commonControlItems = CommonControlItems(self)
        self.positionControlItems = PositionControlItems(self)
        self.transferFunctionControlItems = TransferFunctionControlItems(self)
        self.planeWidgetControlItems = PlaneWidgetControlItems()
        self.playControlItems = PlayControlItems(self)
        self.smoothingControlItems = SmoothingControlItems(self)
        self.lightingControlItems = LightingControlItems()
        self.viewControlItems = ViewControlItems(self)
        self.labelControlItems = LabelControlItems()
        
        
        tabWidget = QTabWidget()
        tabWidget.addTab(self.commonControlItems, "General Controls")
        tabWidget.addTab(self.viewControlItems, "View Controls")
        tabWidget.addTab(self.cropControlItems, "Cropping XYZ")
        tabWidget.addTab(self.planeWidgetControlItems, "Cropping Planes")
        tabWidget.addTab(self.transferFunctionControlItems, "Opacity && Color")
        tabWidget.addTab(self.positionControlItems, "Rotation && Position")
        tabWidget.addTab(self.playControlItems, "Play")
        tabWidget.addTab(self.smoothingControlItems, "Smoothing")
        tabWidget.addTab(self.lightingControlItems, "Lighting")
        tabWidget.addTab(self.labelControlItems, "Labelling")

        
        buttonGroup = QGroupBox()
        self.button_quit = QPushButton("Close")
        self.button_savesettings = QPushButton("Save Settings")
        self.label_loadsettings = QLabel("Load Settings: ")
        self.label_loadsettings.setAlignment(Qt.AlignTrailing)
        self.combobox_loadsettings = QComboBox()
        
        buttonLayout = QGridLayout()
        for index, button in enumerate((self.label_loadsettings, self.combobox_loadsettings, self.button_savesettings, self.button_quit)):
            buttonLayout.addWidget(button, index/2, index % 2 )
        buttonLayout.setSpacing(0)
        buttonLayout.setColumnStretch(0,4)
        buttonLayout.setColumnStretch(1,6)        
        
        buttonGroup.setLayout(buttonLayout)
        
        
        layout = QGridLayout()
        layout.addWidget(self.vtkWidget, 0, 0, 1, 2)
        layout.setRowStretch(0, 10)
        layout.addWidget(tabWidget, 1, 0)
        layout.addWidget(buttonGroup, 1, 1)
        layout.setSpacing(0)
        layout.setMargin(0)
        layout.setColumnStretch(0,10)
        layout.setColumnStretch(1,3)
        
        self.frame.setLayout(layout)
        self.setCentralWidget(self.frame)
        
        self.button_quit.clicked.connect(self.close)
        self.button_loadEcho.clicked.connect(self.loadEcho)
        self.button_box.clicked.connect(self.setBoxWidget)
        self.transferFunctionControlItems.combobox_transfunction.activated.connect(self.updateTFunc)
        self.button_resetcrop.clicked.connect(self.resetCrop)
        self.button_stereo.clicked.connect(self.setStereo)
        self.button_measurement.clicked.connect(self.setMeasurement)
        self.button_anglemeasurement.clicked.connect(self.setAngleMeasurement)
        self.button_loadDir.clicked.connect(self.loadDir)
        self.button_savesettings.clicked.connect(self.saveSettings)
        self.button_iterate.clicked.connect(self.playCardiacCycle)
        self.button_rotate.clicked.connect(self.rotateCamera)
        self.transferFunctionControlItems.button_edittransfunction.clicked.connect(self.editTransferFunction)
        self.transferFunctionControlItems.button_editopacity.clicked.connect(self.editOpacity)
        self.transferFunctionControlItems.button_editcolor.clicked.connect(self.editColor)
        self.transferFunctionControlItems.button_editgradient.clicked.connect(self.editGradientOpacity)
        self.transferFunctionControlItems.button_savetfunction.clicked.connect(self.saveTransferFunction)

        self.button_savescreen.clicked.connect(self.saveScreen)
        self.combobox_loadsettings.activated.connect(self.loadSettings)
        
            
        for scale in (self.scale_xmin, self.scale_xmax, self.scale_ymin, self.scale_ymax, self.scale_zmin, self.scale_zmax):
            scale.valueChanged.connect(self.cropVolume)
            
        for slider in (self.slider_xsmooth,self.slider_ysmooth,self.slider_zsmooth):
            slider.valueChanged.connect(self.smoothVolume)
            
        self.button_nosmooth.clicked.connect(self.setNoSmooth)
        self.button_lowsmooth.clicked.connect(self.setLowSmooth)
        self.button_midsmooth.clicked.connect(self.setMidSmooth)
        self.button_highsmooth.clicked.connect(self.setHighSmooth)            

        self.scale_azimuth.valueChanged.connect(self.setAzimuth)
        self.scale_elevation.valueChanged.connect(self.setElevation)
        self.scale_roll.valueChanged.connect(self.setRoll)
        self.scale_stereodepth.valueChanged.connect(self.setStereoDepth)
        
        self.button_zoomin.clicked.connect(self.zoomIn)
        self.button_zoomout.clicked.connect(self.zoomOut)
        self.button_resetcamera.clicked.connect(self.resetCamera)
        
        self.slider_imageNumber.valueChanged.connect(self.slider_imageNumber_valuechanged)
        
        for i in range(6):
            self.planeWidgetControlItems.button_pwidgets[i].toggled.connect(self.setPlaneWidgets)
            self.planeWidgetControlItems.button_pwidgetreset[i].clicked.connect(self.resetPlaneWidget)
            
        self.planeWidgetControlItems.button_pwdigetresetall.clicked.connect(self.resetAllPlaneWidgets)
        self.button_cameratext.toggled.connect(self.displayCameraOrientation)
        
        self.lightingControlItems.button_shade.toggled.connect(self.setShade)
        self.lightingControlItems.button_interpolation.toggled.connect(self.setInterpolation)
        self.lightingControlItems.button_gradientopacity.toggled.connect(self.setDisableGradientOpacity)
        self.lightingControlItems.slider_ambient.valueChanged.connect(self.adjustLights)
        self.lightingControlItems.slider_diffuse.valueChanged.connect(self.adjustLights)
        self.lightingControlItems.slider_specular.valueChanged.connect(self.adjustLights)
        
        self.lightingControlItems.slider_keylightintensity.valueChanged.connect(self.setKeyLightIntensity)
        
        self.labelControlItems.button_label.toggled.connect(self.displayLabel)
        self.labelControlItems.text_label.textEdited.connect(self.changeLabelText)
        self.labelControlItems.scale_labelsize.valueChanged.connect(self.changeLabelSize)
        self.labelControlItems.combobox_labels.currentIndexChanged[int].connect(self.changeLabelIndex)
                
        for button in self.button_view:
            button.clicked.connect(self.changeView)

        
    def getRenderWindow(self):
        return self.vtkWidget.GetRenderWindow()
    
    
class vtkTimerHeadTrack():
    tracker=vrpn.receiver.Tracker("Tracker0@localhost")
    button=vrpn.receiver.Button("Tracker0@localhost")
    
    
    def __init__(self, cam, text, text2, lineactor, volume, master):
        self.text = text
        self.text2 = text2
        self.tracker.register_change_handler("tracker", self.callback, "position")
        self.button.register_change_handler("button", self.callback_button)
        
        self.lineactor = lineactor
        self.cam = cam
        self.master = master
        self.rmatrix = np.zeros((4,4))
        self.rmatrix4x4 = vtk.vtkMatrix4x4()        
        
        self.button0state = False
        self.button1state = False        
        self.button2state = False
        self.volume = volume
        self.volumeTransform = vtk.vtkTransform()
        self.initialvolumeTransform = None
        
        self.initialZPosition = None
        self.initialScaleTransform = None        
        
        
    def execute(self, obj, event):
        iren = obj
        self.button.mainloop()
        self.tracker.mainloop()           
        iren.GetRenderWindow().Render()   
        
    def callback_button(self, userdata, data):
        if data['button'] == 0:
            if data['state'] == 1:
                self.lineactor.GetProperty().SetColor(1.0,0.0,0.0)
                self.button0state = True
            elif data['state'] == 0:
                self.lineactor.GetProperty().SetColor(1.0,1.0,1.0)
                self.button0state = False                  
        if data['button'] == 1:
            if data['state'] == 1:
                self.lineactor.GetProperty().SetColor(0.0,0.0,1.0)
                self.button1state = True
            elif data['state'] == 0:
                self.lineactor.GetProperty().SetColor(1.0,1.0,1.0)
                self.button1state = False                   
        if data['button'] == 2:
            if data['state'] == 1:
                self.lineactor.GetProperty().SetColor(0.0,1.0,0.0)
                self.button2state = True
            elif data['state'] == 0:
                self.lineactor.GetProperty().SetColor(1.0,1.0,1.0)
                self.button2state = False                             
    
    def callback(self, userdata, data):

        dx, dy, dz = data['position']
        qx, qy, qz, qw = data['quaternion']        
        sensorid = data['sensor']
        
        qwxyz = np.array([qw,qx,qy,qz])        
        vtk.vtkMath.QuaternionToMatrix3x3(qwxyz, self.rmatrix[0:3,0:3])
               
        self.rmatrix[0,3] = 1000*dx
        self.rmatrix[1,3] = 1000*dy
        self.rmatrix[2,3] = 1000*dz
        self.rmatrix[3,3] = 1.0
        
        self.rmatrix = camMat4x4.dot(self.rmatrix)
        
        if sensorid == 0:
            self.text.SetInput("pos = (%-#6.3g, %-#6.3g, %-#6.3g)\n quaternion = (%-#6.3g, %-#6.3g, %-#6.3g, %-#6.3g)" % (dx, dy, dz, qw, qx, qy, qz))
    
            if not math.isnan(dx) and not math.isnan(qx):
                self.cam.SetEyeTransformMatrix(self.rmatrix.reshape(16,1))
                
                
        elif sensorid == 1:
            
            transform = vtk.vtkTransform()
            
            self.rmatrix4x4.DeepCopy(self.rmatrix.reshape(16,1))
            
            transform.PostMultiply()
            transform.Concatenate(self.rmatrix4x4)            
            
            transformCam = vtk.vtkTransform()            
            transformCam.Concatenate(self.rmatrix4x4)    
            
            if self.button0state:
                               
                stylusTransform = vtk.vtkTransform()        
                stylusTransform.Concatenate(transformCam)               
 
                if self.initialCameraTransformMatrix:
                    stylusTransform.Concatenate(self.initialCameraTransformMatrix.GetInverse())
                     
                if self.initialCameraUserViewTransform:
                    stylusTransform.Concatenate(self.initialCameraUserViewTransform)
                
                stylusTransform.Update()                
                self.cam.SetUserViewTransform(stylusTransform)
                self.cam.Modified()
                
                
            else:
                self.initialCameraTransformMatrix = transformCam
                self.initialCameraUserViewTransform = self.cam.GetUserViewTransform()
                modeltransform = vtk.vtkTransform()
                modeltransform.Concatenate(self.cam.GetModelViewTransformMatrix())                
                transform.Concatenate(modeltransform.GetInverse())                           
                self.lineactor.SetUserTransform(transform)
                self.lineactor.Modified()     
                
                
            if self.button1state:
                if self.initialZPosition:
                    scaleTransform = vtk.vtkTransform()
                    scale = (1 + 5*(dz - self.initialZPosition))
                    
                    if self.initialScaleTransform:
                        scaleTransform.Concatenate(self.initialScaleTransform)

                    scaleTransform.Scale(scale, scale, scale)
                    self.cam.SetUserViewTransform(scaleTransform)
                    self.cam.Modified()                        

            else:
                self.initialZPosition = dz
                self.initialScaleTransform = self.cam.GetUserViewTransform()  
                
            if self.button2state:
                if self.master.distanceWidget.GetEnabled():
                    self.distanceWidgetInteraction(transform)
                elif self.master.angleWidget.GetEnabled():
                    self.angleWidgetInteraction(transform)    
                else:
                    self.planeWidgetInteraction(transform)   

            self.text2.SetInput("pos = (%-#6.3g, %-#6.3g, %-#6.3g)\n quaternion = (%-#6.3g, %-#6.3g, %-#6.3g, %-#6.3g)" % (self.rmatrix4x4.GetElement(0, 3), self.rmatrix4x4.GetElement(1, 3), self.rmatrix4x4.GetElement(2, 3), qw, qx, qy, qz))

    def distanceWidgetInteraction(self, transform):
        pt, pt1, pt2 = np.empty((3)), np.empty((3)), np.empty((3))
         
        transform.TransformPoint(np.array([0,0,-100]),pt)
         
        self.master.distanceWidget.GetDistanceRepresentation().GetPoint1WorldPosition(pt1)
        self.master.distanceWidget.GetDistanceRepresentation().GetPoint2WorldPosition(pt2)
         
        if np.linalg.norm(pt-pt1) < np.linalg.norm(pt-pt2):                
            self.master.distanceWidget.GetDistanceRepresentation().SetPoint1WorldPosition(pt)
        else:
            self.master.distanceWidget.GetDistanceRepresentation().SetPoint2WorldPosition(pt)   
            
        self.master.distanceText.SetInput("distance = %-#6.3g mm" % self.master.distanceWidget.GetDistanceRepresentation().GetDistance()) 
        
    def angleWidgetInteraction(self, transform):
        pt, pt1, pt2, pt3 = [np.empty((3)) for i in range(4)]
        
        transform.TransformPoint(np.array([0,0,-100]),pt)
        
        self.master.angleWidget.GetAngleRepresentation().GetPoint1WorldPosition(pt1)
        self.master.angleWidget.GetAngleRepresentation().GetCenterWorldPosition(pt2)
        self.master.angleWidget.GetAngleRepresentation().GetPoint2WorldPosition(pt3)
        
        if np.linalg.norm(pt-pt1) <= np.linalg.norm(pt-pt2) and np.linalg.norm(pt-pt1) <= np.linalg.norm(pt-pt3):
            self.master.angleWidget.GetAngleRepresentation().SetPoint1WorldPosition(pt)
        elif np.linalg.norm(pt-pt2) <= np.linalg.norm(pt-pt1) and np.linalg.norm(pt-pt2) <= np.linalg.norm(pt-pt3):
            self.master.angleWidget.GetAngleRepresentation().SetCenterWorldPosition(pt)
        elif np.linalg.norm(pt-pt3) <= np.linalg.norm(pt-pt1) and np.linalg.norm(pt-pt3) <= np.linalg.norm(pt-pt2):
            self.master.angleWidget.GetAngleRepresentation().SetPoint2WorldPosition(pt)
            
        self.master.angleText.SetInput("angle = %-#6.3g degrees" % vtk.vtkMath.DegreesFromRadians(self.master.angleWidget.GetAngleRepresentation().GetAngle()))            
                                    
        
    def planeWidgetInteraction(self, transform):
        pt, normal_ = np.empty((3)), np.empty((3))
        transform.TransformPoint(np.array([0,0,-100]),pt)
        transform.TransformNormal(np.array([0,0,-1.0]),normal_)
        
        for i in range(6):
            if self.master.planeWidget[i].GetEnabled():
                self.master.planeWidget[i].SetOrigin(pt)
                self.master.planeWidget[i].SetNormal(normal_)
                self.master.planeWidget[i].UpdatePlacement() 
                
                break
            
        self.master.pwCallback(None,None)
        
        

class vtkTimerSpaceNav():
    analog=vrpn.receiver.Analog("device0@localhost")
    
    def __init__(self, ren):
        self.timer_count = 0
        self.ren = ren
        self.cam = self.ren.GetActiveCamera()
        self.transform = vtk.vtkTransform()
        self.analog.register_change_handler("analog", self.callback)
        
    def execute(self, obj, event):
        iren = obj
        self.analog.mainloop()
            
        iren.GetRenderWindow().Render()    
    
    def callback(self,userdata, data):
        ch = data['channel']
        self.cam.Azimuth(ch[5])
        self.cam.Elevation(ch[3])
        self.cam.Roll(ch[4])
        self.cam.OrthogonalizeViewUp()
        self.cam.ApplyTransform(self.transform)
        self.ren.ResetCameraClippingRange()


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

class SmoothingControlItems(QWidget):
    def __init__(self, master):
        super(SmoothingControlItems, self).__init__()    
        
        master.button_nosmooth = QPushButton('No Smoothing')
        master.button_lowsmooth = QPushButton('Low Smoothing')
        master.button_midsmooth = QPushButton('Medium Smoothing')
        master.button_highsmooth = QPushButton('High Smoothing')
        
        master.slider_xsmooth = QSlider(Qt.Horizontal)    
        master.slider_ysmooth = QSlider(Qt.Horizontal)
        master.slider_zsmooth = QSlider(Qt.Horizontal)
        
        master.label_xsmooth = QLabel('')
        master.label_ysmooth = QLabel('')
        master.label_zsmooth = QLabel('')

        layout = QGridLayout() 
        
        for index, button in enumerate((master.button_nosmooth, master.button_lowsmooth, master.button_midsmooth, master.button_highsmooth)):
            layout.addWidget(button, 1, index)
        
        layout.addWidget(master.label_xsmooth,0,index+1)
        layout.addWidget(master.label_ysmooth,0,index+2)
        layout.addWidget(master.label_zsmooth,0,index+3)
        
        layout.addWidget(master.slider_xsmooth,1,index+1)
        layout.addWidget(master.slider_ysmooth,1,index+2)
        layout.addWidget(master.slider_zsmooth,1,index+3)
        
        
        layout.setMargin(5)
        
        self.setLayout(layout) 
        
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
                   
class CommonControlItems(QWidget):
    def __init__(self, master):
        self.master = master
        super(CommonControlItems, self).__init__()
        
        nbuttons = 8
        
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
        
class PositionControlItems(QWidget):
    def __init__(self, master):
        self.master = master        
        super(PositionControlItems, self).__init__()

        nscales = 4
        master.scale_azimuth, master.scale_elevation, master.scale_roll = [QDial() for i in range(nscales-1)]
        master.scale_stereodepth = QScrollBar(Qt.Horizontal)
        label_azimuth, label_elevation, label_roll, label_stereodepth = [QLabel() for i in range(nscales)]
        master.button_zoomin, master.button_zoomout, master.button_resetcamera = [QPushButton() for i in range(3)]
        label_stereodepth = QLabel("Stereo depth")
        
        for button, buttontext in zip((master.button_zoomin, master.button_zoomout, master.button_resetcamera),("Zoom In", "Zoom Out", "Reset")):
            button.setText(buttontext)
        
        layout = QGridLayout()
        for index, label, labeltext in zip(range(nscales), (label_azimuth, label_elevation, label_roll), ("Azimuth", "Elevation", "Roll")):
            label.setText(labeltext)
            label.setAlignment(Qt.AlignRight)
        
        layout.addWidget(master.button_zoomin, 0, 7)
        layout.addWidget(master.button_zoomout, 0, 8)
        
        for index, scale in enumerate((master.scale_azimuth, master.scale_elevation, master.scale_roll)):
            scale.setMinimum(-179)
            scale.setMaximum(180)
            scale.setValue(0)
            scale.setMaximumSize(QSize(60,60))
            
        for index, comp in enumerate((label_azimuth, master.scale_azimuth,label_elevation,  master.scale_elevation, label_roll, master.scale_roll)):
            layout.addWidget(comp,0,index, 2, 1)
        
        layout.addWidget(master.button_resetcamera, 1, 8)
            
        master.scale_stereodepth.setValue(20)            
        master.scale_stereodepth.setMinimum(10)
        master.scale_stereodepth.setMaximum(100)
        layout.addWidget(label_stereodepth,0,6)            
        layout.addWidget(master.scale_stereodepth,1,6)
        
        layout.setMargin(0)
        layout.setHorizontalSpacing(20)       
        layout.setVerticalSpacing(0)     
        
        for col, val in enumerate((1,2,1,2,1,2,4,4,4)):
            layout.setColumnStretch(col,val)
                    
        self.setLayout(layout)
        
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

class vtkTimerCallBack():
    def __init__(self, K, isplay, isrotate, slider_imageNumber):
        self.timer_count = 0
        self.K = K
        self.isplay = isplay
        self.isrotate = isrotate
        self.slider_imageNumber = slider_imageNumber
        
    def execute(self, obj, event):
        iren = obj
        if self.isplay: 
            self.slider_imageNumber.setValue(self.timer_count % self.K)
            self.timer_count += 1
            
        if self.isrotate:
            self.renderer.GetActiveCamera().Azimuth(-1)  
            
        iren.GetRenderWindow().Render()
        
    def setplay(self, isplay):
        self.isplay = isplay
        
    def setrotate(self, isrotate):
        self.isrotate = isrotate         

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

class GradientOpacityEditor(QDialog):
    def __init__(self, volumeProperty, reader, renWin):
        super(GradientOpacityEditor, self).__init__()  
        self.volumeProperty = volumeProperty
        self.reader = reader
        self.renWin = renWin
        self.setWindowTitle("Gradient Opacity Editor") 
        self.opacityfunction =  self.volumeProperty.GetGradientOpacity(0)
        self.npts = self.opacityfunction.GetSize()
        
        self.vScale = [[QSlider(Qt.Horizontal) for i in range(4)] for j in range(self.npts)]  
        self.label_value = [[QLabel(" ") for i in range(4)] for j in range(self.npts)]  
        
        label_scaleName = [QLabel() for j in range(4)]
        for j, text in enumerate(("Intensity", " Opacity","Midpoint","Sharpness")):
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
            
        self.volumeProperty.SetGradientOpacity(self.opacityfunction)
        self.renWin.Render()   
        
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
               
class TransferFunctionEditor(pysideQWidget): 
    def __init__(self, volumeProperty, reader, renWin):        
        super(TransferFunctionEditor, self).__init__()    
        self.volumeProperty = volumeProperty
        self.reader = reader
        self._renderWindow = renWin
        self.setWindowTitle("Transfer Function Editor") 
        
        self.opacityfunction =  self.volumeProperty.GetScalarOpacity(0)
        self.colorfunction =  self.volumeProperty.GetRGBTransferFunction(0)

        self.npts = self.opacityfunction.GetSize()
        
        imageData = reader.GetOutput()
        self.histogramWidget = TransferFunctionWidget()
        transferFunction = TransferFunction()
        
        rmax = self.reader.GetOutput().GetScalarRange()[1] 
        rmin = self.reader.GetOutput().GetScalarRange()[0]         
        transferFunction.setRange([rmin, rmax])
        
        self.minimum, self.maximum = rmin, rmax
        
        opacityNode = np.empty((4,))
        transferFunction.addPoint(rmin, self.opacityfunction.GetValue(rmin), color=[self.colorfunction.GetRedValue(rmin), self.colorfunction.GetGreenValue(rmin), self.colorfunction.GetBlueValue(rmin)])
        for i in range(self.npts):
            self.opacityfunction.GetNodeValue(i, opacityNode)
            if (opacityNode[0] > rmin) and (opacityNode[0] < rmax):
                transferFunction.addPoint(opacityNode[0], opacityNode[1], color=[self.colorfunction.GetRedValue(opacityNode[0]), self.colorfunction.GetGreenValue(opacityNode[0]), self.colorfunction.GetBlueValue(opacityNode[0])])       
            
        transferFunction.addPoint(rmax, self.opacityfunction.GetValue(rmax), color=[self.colorfunction.GetRedValue(rmax), self.colorfunction.GetGreenValue(rmax), self.colorfunction.GetBlueValue(rmax)])
        
        transferFunction.updateTransferFunction() 
        
        self.histogramWidget.transferFunction = transferFunction 
        self.histogramWidget.setImageData(imageData)        
        self.histogramWidget.transferFunction.updateTransferFunction()        
        self.histogramWidget.updateNodes()  
        
        self.histogramWidget.valueChanged.connect(self.valueChanged)

        self.resize(400,300)
        
    def getTransferFunctionWidget(self):
        return self.histogramWidget        
    
    def updateTransferFunction(self):
        if self.histogramWidget:
            self.histogramWidget.transferFunction.updateTransferFunction()
            self.colorFunction = self.histogramWidget.transferFunction.colorFunction
            self.opacityFunction = self.histogramWidget.transferFunction.opacityFunction
        else:
            # Transfer functions and properties
            self.colorFunction = vtkColorTransferFunction()
            self.colorFunction.AddRGBPoint(self.minimum, 0, 0, 0)
            self.colorFunction.AddRGBPoint(self.maximum, 0, 0, 0)

            self.opacityFunction = vtkPiecewiseFunction()
            self.opacityFunction.AddPoint(self.minimum, 0)
            self.opacityFunction.AddPoint(self.maximum, 0)

        self.volumeProperty.SetColor(self.colorFunction)
        self.volumeProperty.SetScalarOpacity(self.opacityFunction)

        self._renderWindow.Render() 
        
    def valueChanged(self, value):
        self.updateTransferFunction()
        
class TDVizCustom(TDViz):      
    def __init__(self, parent=None):
        TDViz.__init__(self, parent)
        
        self._renWin = self.getRenderWindow()
        self._renWin.StereoCapableWindowOn()
        self._renWin.SetStereoTypeToCrystalEyes()
        self._renWin.StereoRenderOn()  
        
        self._ren = vtk.vtkRenderer()
        self.volume = vtk.vtkVolume()
        self.volumeProperty = vtk.vtkVolumeProperty()        
        
        self._renWin.AddRenderer(self._ren)
        
        self._iren = self._renWin.GetInteractor()  
        self._iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())
        self.removeAllMouseEvents(self._iren)
        
        self.sopuid = []
        self.reader = []
        
        self.initAxes()  
        self.initBoxWidget()
        self.initMeasurementTool()
        self.initAngleMeasurementTool()
        self.initPlaneWidget()
        self.initSphereWidget()
        self.initLabels()
        
        tfuncs = glob.glob1(tfuncdir, "*.vvt")
        self.transferFunctionControlItems.combobox_transfunction.addItems(tfuncs)        

        self.varscaleazimuth = self.scale_azimuth.value()
        self.varscaleelevation = self.scale_elevation.value()

        self._ren.GetActiveCamera().AddObserver("AnyEvent", self.cameraAnyEvent)
        
        self.imageGaussianSmooth = vtk.vtkImageGaussianSmooth()
        
        self._renWin.Render()  

        self.cam = self._ren.GetActiveCamera()
        self.cam.UseOffAxisProjectionOn()
        
#         self.cam.SetScreenBottomLeft(-262.5,-148.5,-410)
#         self.cam.SetScreenBottomRight(262.5,-148.5,-410)
#         self.cam.SetScreenTopRight(262.5,148.5,-410)    

        self.cam.SetUseOffAxisProjection(1)
        self.cam.SetEyeSeparation(60)        
        
        
        
        
        self.initHeadTrackText()
        
        self._renWin.Render()  
        
    def removeAllMouseEvents(self, obj):        
        obj.RemoveObservers('LeftButtonPressEvent')
        obj.RemoveObservers('RightButtonPressEvent')
        obj.RemoveObservers('ButtonPressEvent')
        obj.RemoveObservers('LeftButtonReleaseEvent')
        obj.RemoveObservers('RightButtonReleaseEvent')
        obj.RemoveObservers('ButtonReleaseEvent')
        obj.RemoveObservers('MouseMoveEvent')
        obj.RemoveObservers('MouseWheelForwardEvent')
        obj.RemoveObservers('MouseWheelBackwardEvent')
        obj.RemoveObservers('MouseMoveEvent')        
        
    def initHeadTrackText(self):
        self.headtracktext = vtk.vtkTextActor()        
        self.headtracktext.SetDisplayPosition(20, 20)      
        self.headtracktext.SetInput("0")
        self._ren.AddActor(self.headtracktext)  

        self.stylustext = vtk.vtkTextActor()        
        self.stylustext.SetDisplayPosition(1600, 20)      
        self.stylustext.SetInput("0")
        self._ren.AddActor(self.stylustext)  
        
    def initStylus(self):
        sphere = vtk.vtkSphereSource()
        sphere.SetThetaResolution(30)
        sphere.SetPhiResolution(30)
        sphere.SetRadius(2)

        sphereTransform = vtk.vtkTransform()
        sphereTransform.Translate(0, 0, -100)        
        
        sphereTransformFilter = vtk.vtkTransformPolyDataFilter()
        sphereTransformFilter.SetInputConnection(sphere.GetOutputPort())
        sphereTransformFilter.SetTransform(sphereTransform)
        
        line = vtk.vtkLineSource()
        line.SetResolution(30)
        line.SetPoint1(0.0, 0.0, 0.0)
        line.SetPoint2(0.0, 0.0, -100)
        
        appendFilter = vtk.vtkAppendPolyData()
        appendFilter.AddInputConnection(line.GetOutputPort())
        appendFilter.AddInputConnection(sphereTransformFilter.GetOutputPort())
        
        
        lineMapper = vtk.vtkPolyDataMapper()
        lineMapper.SetInputConnection(appendFilter.GetOutputPort())
        
        self.stylusactor = vtk.vtkActor()
        self.stylusactor.SetMapper(lineMapper)    
        
        self._ren.AddActor(self.stylusactor)
        
       
    def cameraAnyEvent(self,obj,evt):
        self.cameraText.SetInput("Orientation X = %5.0f\nOrientation Y = %5.0f\nOrientation Z = %5.0f" % (obj.GetOrientation()[0],obj.GetOrientation()[1],obj.GetOrientation()[2]))
    
    def initAxes(self):
        self.axes = vtk.vtkAxesActor()
        self.axesWidget = vtk.vtkOrientationMarkerWidget()
        self.axes.AxisLabelsOff()
        self.axes.SetShaftTypeToCylinder()
        
        self.axesWidget.SetOrientationMarker(self.axes)
        self.axesWidget.SetInteractor(self._iren)
        self.axesWidget.SetViewport(0.0, 0.0, 0.15, 0.15)
        self.axesWidget.SetEnabled(1)
        self.axesWidget.InteractiveOff()   
             
        self.cameraText = vtk.vtkTextActor()        
        self.cameraText.SetTextScaleModeToProp()
        self.cameraText.SetDisplayPosition(10, 10)
        
    def initBoxWidget(self):
        self.boxWidget = vtk.vtkBoxWidget()
        self.boxWidget.SetInteractor(self._iren)
        self.boxWidget.SetPlaceFactor(1.0)
        self.boxWidget.SetHandleSize(0.004)
        self.boxWidget.InsideOutOn()
        self.boxWidget.AddObserver("StartInteractionEvent", self.bwStartInteraction)
        self.boxWidget.AddObserver("InteractionEvent", self.bwClipVolumeRender)
        self.boxWidget.AddObserver("EndInteractionEvent", self.bwEndInteraction) 
        self.planes = vtk.vtkPlanes()
                
    def initPlaneWidget(self):
        self.planeWidget = [vtk.vtkImplicitPlaneWidget() for i in range(6)]
        self.pwPlane = [vtk.vtkPlane() for i in range(6)]
        self.pwClippingPlanes = vtk.vtkPlaneCollection()
              
        for i in range(6):
            self.planeWidget[i].SetInteractor(self._iren)
            self.planeWidget[i].SetPlaceFactor(1.1)
            self.planeWidget[i].TubingOff()
            self.planeWidget[i].DrawPlaneOff()
            self.planeWidget[i].OutsideBoundsOff()  
            self.planeWidget[i].OutlineTranslationOff() 
            self.planeWidget[i].ScaleEnabledOff()
            self.planeWidget[i].SetHandleSize(0.25*self.planeWidget[i].GetHandleSize())
            self.planeWidget[i].SetKeyPressActivationValue(str(i+1))
            self.planeWidget[i].SetInteractor(self._iren)
            self.planeWidget[i].AddObserver("InteractionEvent", self.pwCallback)  
            self.pwClippingPlanes.AddItem(self.pwPlane[i])
            
    def initSphereWidget(self):
        self.lightkit = vtk.vtkLightKit()
        self.lightkit.SetKeyLightIntensity(2.0)
        self.lightkit.MaintainLuminanceOn()
        
        print self.lightkit.GetBackLightWarmth(), self.lightkit.GetFillLightWarmth(), self.lightkit.GetHeadLightWarmth()
        
        self.lightkit.AddLightsToRenderer(self._ren)
        
    def initLabels(self):
        nlabels = self.labelControlItems.combobox_labels.count()
        self.labelText = [vtk.vtkVectorText() for i in range(nlabels)]
        self.labelMapper = [vtk.vtkPolyDataMapper() for i in range(nlabels)]
        self.labelActor = [vtk.vtkFollower() for i in range(nlabels)]
        self.labelLine = [vtk.vtkLineWidget2() for i in range(nlabels)]
        self.labelLineRep = [vtk.vtkLineRepresentation() for i in range(nlabels)]
        
        for i in range(nlabels):            
            self.labelText[i].SetText("Label"+str(i+1))
            
            self.labelMapper[i].SetInputConnection(self.labelText[i].GetOutputPort())
            
            self.labelActor[i].SetMapper(self.labelMapper[i])
            self.labelActor[i].SetScale(2.0)            
            self.labelActor[i].GetProperty().SetColor(1,0,0) 
            
            self.labelLineRep[i].SetHandleSize(0)
            
            self.labelLine[i].SetRepresentation(self.labelLineRep[i])            
            self.labelLine[i].SetInteractor(self._iren)
            self.labelLine[i].AddObserver("StartInteractionEvent", self.labelBeginInteraction)
            self.labelLine[i].AddObserver("InteractionEvent", self.labelEndInteraction)        
            
            
            self.labelActor[i].SetCamera(self._ren.GetActiveCamera())
           
    def labelBeginInteraction(self, obj,evt):
        nlabels = self.labelControlItems.combobox_labels.count()
        for i in range(nlabels):
            self.labelActor[i].SetPosition(self.labelLine[i].GetLineRepresentation().GetPoint2WorldPosition())
        
    def labelEndInteraction(self, obj,evt):
        nlabels = self.labelControlItems.combobox_labels.count()
        for i in range(nlabels):
            self.labelActor[i].SetPosition(self.labelLine[i].GetLineRepresentation().GetPoint2WorldPosition())
            
    def resetAllPlaneWidgets(self):
        if self.reader:
            xmin, xmax, ymin, ymax, zmin, zmax = self.reader.GetOutput().GetBounds()
                
            self.planeWidget[0].SetOrigin(0,ymax/2.,zmax/2.)
            self.planeWidget[0].SetNormal(1,0,0)
            self.planeWidget[0].UpdatePlacement() 
    
            self.planeWidget[1].SetOrigin(xmax/2.,0,zmax/2.)
            self.planeWidget[1].SetNormal(0,1,0)
            self.planeWidget[1].UpdatePlacement() 
    
            self.planeWidget[2].SetOrigin(xmax/2.,ymax/2.,0)
            self.planeWidget[2].SetNormal(0,0,1)
            self.planeWidget[2].UpdatePlacement() 
            
    
            self.planeWidget[3].SetOrigin(xmax,ymax/2.,zmax/2.)
            self.planeWidget[3].SetNormal(-1,0,0)
            self.planeWidget[3].UpdatePlacement() 
    
            self.planeWidget[4].SetOrigin(xmax/2.,ymax,zmax/2.)
            self.planeWidget[4].SetNormal(0,-1,0)
            self.planeWidget[4].UpdatePlacement() 
    
            self.planeWidget[5].SetOrigin(xmax/2.,ymax/2.,zmax)
            self.planeWidget[5].SetNormal(0,0,-1)
            self.planeWidget[5].UpdatePlacement() 
                
            self.pwCallback(self, None)
            self._renWin.Render()
            
    def resetPlaneWidget(self):
        if self.reader:
            
            sendername = self.sender().objectName()            
            
            xmin, xmax, ymin, ymax, zmin, zmax = self.reader.GetOutput().GetBounds()
            
            if sendername == "resetplane0":                
                self.planeWidget[0].SetOrigin(0,ymax/2.,zmax/2.)
                self.planeWidget[0].SetNormal(1,0,0)
                self.planeWidget[0].UpdatePlacement() 
            elif sendername == "resetplane1":
                self.planeWidget[1].SetOrigin(xmax/2.,0,zmax/2.)
                self.planeWidget[1].SetNormal(0,1,0)
                self.planeWidget[1].UpdatePlacement() 
            elif sendername == "resetplane2":        
                self.planeWidget[2].SetOrigin(xmax/2.,ymax/2.,0)
                self.planeWidget[2].SetNormal(0,0,1)
                self.planeWidget[2].UpdatePlacement() 
            elif sendername == "resetplane3":
                self.planeWidget[3].SetOrigin(xmax,ymax/2.,zmax/2.)
                self.planeWidget[3].SetNormal(-1,0,0)
                self.planeWidget[3].UpdatePlacement() 
            elif sendername == "resetplane4":
                self.planeWidget[4].SetOrigin(xmax/2.,ymax,zmax/2.)
                self.planeWidget[4].SetNormal(0,-1,0)
                self.planeWidget[4].UpdatePlacement() 
            elif sendername == "resetplane5":        
                self.planeWidget[5].SetOrigin(xmax/2.,ymax/2.,zmax)
                self.planeWidget[5].SetNormal(0,0,-1)
                self.planeWidget[5].UpdatePlacement() 
                
            self.pwCallback(self, None)
            self._renWin.Render()            
           
    def displayCameraOrientation(self):
        if self.button_cameratext.isChecked():
            self._ren.AddActor(self.cameraText)
        else:
            self._ren.RemoveActor(self.cameraText)
            
        self._renWin.Render()
            
    def pwCallback(self, obj, evt):
        self.volumeMapper.RemoveAllClippingPlanes()
        self.pwClippingPlanes.RemoveAllItems()

        for i in range(6):
            self.planeWidget[i].GetPlane(self.pwPlane[i])
            self.pwClippingPlanes.AddItem(self.pwPlane[i])   
            
        self.volumeMapper.SetClippingPlanes(self.pwClippingPlanes) 
        
    def initMeasurementTool(self):
        self.distanceRep = vtk.vtkDistanceRepresentation3D()
        self.distanceRep.SetLabelFormat("%-#6.3g mm")
        
        self.distanceWidget = vtk.vtkDistanceWidget()
        self.distanceWidget.SetInteractor(self._iren)
        self.distanceWidget.SetWidgetStateToManipulate()
        self.distanceWidget.CreateDefaultRepresentation()
        self.distanceWidget.SetRepresentation(self.distanceRep)
        self.distanceWidget.SetEnabled(0)  
        self.removeAllMouseEvents(self.distanceWidget)
        
        self.distanceWidget.AddObserver("StartInteractionEvent", self.dwStartInteraction)
        self.distanceWidget.AddObserver("InteractionEvent", self.dwUpdateMeasurement)
        self.distanceWidget.AddObserver("EndInteractionEvent", self.dwEndInteraction)   
        
        self.distanceText = vtk.vtkTextActor()        
        self.distanceText.SetDisplayPosition(900, 10)
        self.distanceText.SetInput("distance = ")    

    def initAngleMeasurementTool(self):
        self.angleRep = vtk.vtkAngleRepresentation3D()
        
        self.angleWidget = vtk.vtkAngleWidget()
        self.angleWidget.SetInteractor(self._iren)
        self.angleWidget.SetWidgetStateToManipulate()
        self.angleWidget.CreateDefaultRepresentation()
        self.angleWidget.SetRepresentation(self.angleRep)
        self.angleWidget.SetEnabled(0)
        
        self.angleWidget.AddObserver("StartInteractionEvent", self.awStartInteraction)
        self.angleWidget.AddObserver("InteractionEvent", self.awUpdateMeasurement)
        self.angleWidget.AddObserver("EndInteractionEvent", self.awEndInteraction)   

        self.angleText = vtk.vtkTextActor()        
        self.angleText.SetDisplayPosition(900, 20)  

        self.angleText.SetInput("angle = ")           
           
    def dwStartInteraction(self, obj, event):
        self._renWin.SetDesiredUpdateRate(10)
    
    def dwEndInteraction(self, obj, event):
        self.distanceText.SetInput("distance = %-#6.3g mm" % obj.GetDistanceRepresentation().GetDistance())        
        self._renWin.SetDesiredUpdateRate(0.001)        
        
    def dwUpdateMeasurement(self, obj, event):
        self.distanceText.SetInput("distance = %-#6.3g mm" % obj.GetDistanceRepresentation().GetDistance())  

    def awStartInteraction(self, obj, event):
        self._renWin.SetDesiredUpdateRate(10)
    
    def awEndInteraction(self, obj, event):
        self.angleText.SetInput("angle = %-#6.3g degrees" % vtk.vtkMath.DegreesFromRadians(obj.GetAngleRepresentation().GetAngle()))        
        self._renWin.SetDesiredUpdateRate(0.001)        
        
    def awUpdateMeasurement(self, obj, event):
        self.angleText.SetInput("angle = %-#6.3g degrees" % vtk.vtkMath.DegreesFromRadians(obj.GetAngleRepresentation().GetAngle()))     

    def getVolumeMapper(self):
        return self.volumeMapper
        
    def getRendererWindow(self):
        return self._renWin

    def getRenderer(self):
        return self._ren
    
    def getRendererWindowInteractor(self):
        return self._iren
    
    def setReader(self,reader):
        self.reader = reader
        
    def setVolumeDimension(self,dim):
        self.dim = dim
        
    def setVolumeSpacing(self,spacing):
        self.spacing = spacing
        
    def setVolumeMapper(self,volumeMapper):
        self.volumeMapper = volumeMapper
              
    def bwStartInteraction(self, obj, event):
        self._renWin.SetDesiredUpdateRate(10)
    
    def bwEndInteraction(self, obj, event):
        self._renWin.SetDesiredUpdateRate(0.001)
    
    def bwClipVolumeRender(self, obj, event):
        obj.GetPlanes(self.planes)
        self.volumeMapper.SetClippingPlanes(self.planes)  
        
    def read_Philips_echo_volume(self,filename):
        header = dicom.read_file(filename)
        spacing_x, spacing_y, spacing_z = header.PhysicalDeltaX, header.PhysicalDeltaY, header[0x3001, 0x1003].value
        dim_x, dim_y, dim_z, number_of_frames = header.Columns, header.Rows, header[0x3001, 0x1001].value, header.NumberOfFrames
        raw = np.fromstring(header.PixelData, dtype=np.uint8)
        return np.reshape(raw, (dim_x, dim_y, dim_z, number_of_frames), order="F"), (10*spacing_x, 10*spacing_y, 10*spacing_z), header.SOPInstanceUID
    
    def loadEcho(self):        
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fname = QFileDialog.getOpenFileName(self,"Select DICOM File",initfdir,"All Files (*);;Text Files (*.txt)", "", options)        
        
        if self.fname:
            
            self.volT = []
            self.cb = []            
            
            self.volT, self.spacing, self.sopuid = self.read_Philips_echo_volume(str(self.fname))
            self.dim = self.volT.shape
            
            vol = self.volT[:, :, :, 0]
            
            self.reader = vtk.vtkImageImport()
            data_string = vol.flatten("A")
            self.reader.CopyImportVoidPointer(data_string, len(data_string))
            self.reader.SetDataScalarTypeToUnsignedChar()
            self.reader.SetNumberOfScalarComponents(1)
            self.reader.SetDataExtent(0, self.dim[0] - 1, 0, self.dim[1] - 1, 0, self.dim[2] - 1)
            self.reader.SetWholeExtent(0, self.dim[0] - 1, 0, self.dim[1] - 1, 0, self.dim[2] - 1)
            self.reader.SetDataSpacing(self.spacing[0], self.spacing[1], self.spacing[2]) 
            
 
            self.volumeMapper = vtk.vtkOpenGLVolumeTextureMapper3D()
            self.volumeMapper.SetPreferredMethodToNVidia()
            self.volumeMapper.SetSampleDistance(0.5)
            
            self.volume.SetMapper(self.volumeMapper)  
            
            self.imageGaussianSmooth.SetInputConnection(self.reader.GetOutputPort()) 
            self.imageGaussianSmooth.Update()
                    
            self.volumeMapper.SetInputConnection(self.imageGaussianSmooth.GetOutputPort())
    
            self.loadData()
            
            self._ren.AutomaticLightCreationOff()
            
            self.isplay = False
            self.isrotate = False
            
            self.slider_imageNumber.setEnabled(True)
            self.button_iterate.setEnabled(True)             
             
            self.slider_imageNumber.setMaximum(self.volT.shape[3]-1)
            self.slider_imageNumber.setValue(0)
            self.slider_imageNumber_valuechanged()
            self.cb = vtkTimerCallBack(self.volT.shape[3], self.isplay, self.isrotate, self.slider_imageNumber)
            
            self.cb.renderer = self._ren
    
    def loadDir(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog
        self.dirname = str(QFileDialog.getExistingDirectory(self,"Select DICOM Directory", initddir, options))
        
        if self.dirname:
            subdir = [name for name in os.listdir(self.dirname) if os.path.isdir(os.path.join(self.dirname, name))]            
            while subdir and self.dirname:
                self.dirname = str(QFileDialog.getExistingDirectory(self, "Select DICOM Directory", self.dirname, options))
                if (self.dirname):
                    subdir = [name for name in os.listdir(self.dirname) if os.path.isdir(os.path.join(self.dirname, name))]        
                
        if self.dirname:
            self._iren.RemoveObservers('TimerEvent')
            
            self.volT = []
            self.cb = []            
            
            self.reader = vtk.vtkDICOMImageReader()
            self.reader.SetDirectoryName(self.dirname)
            self.reader.Update()
            
            self.spacing, self.sopuid = self.reader.GetOutput().GetSpacing(), self.reader.GetStudyUID()
            self.dim = self.reader.GetOutput().GetDimensions()           


            
#             self.volumeMapper = vtk.vtkFixedPointVolumeRayCastMapper()
#             self.volumeMapper = vtk.vtkOpenGLGPUVolumeRayCastMapper()
            
            self.volumeMapper = vtk.vtkVolumeTextureMapper3D()

            self.volumeMapper.SetPreferredMethodToNVidia()
            self.volumeMapper.SetSampleDistance(0.5)

            self.volume.SetMapper(self.volumeMapper)  
            
            self.imageGaussianSmooth.SetInputConnection(self.reader.GetOutputPort()) 
            self.imageGaussianSmooth.Update()
                    
            self.volumeMapper.SetInputConnection(self.imageGaussianSmooth.GetOutputPort())
                        
            self.slider_imageNumber.setEnabled(False)
            self.slider_imageNumber.setValue(0)
            self.button_iterate.setEnabled(False)  
            
            self.loadData()
               
    def resetBoxWidget(self):
        self.volumeMapper.RemoveAllClippingPlanes()
        self.boxWidget.PlaceWidget() 
    
    def loadData(self):
        self._ren.AddVolume(self.volume)
        self.volume.SetMapper(self.volumeMapper)
        self.volume.SetProperty(self.volumeProperty)   
                        
        if vtk.VTK_VERSION < '6':
            self.boxWidget.SetInput(self.reader.GetOutput())
        else:
            self.boxWidget.SetInputConnection(self.reader.GetOutputPort())
            
        for i in range(6):
            if vtk.VTK_VERSION < '6':
                self.planeWidget[i].SetInput(self.reader.GetOutput())
            else:
                self.planeWidget[i].SetInputConnection(self.reader.GetOutputPort())
                
            self.planeWidget[i].PlaceWidget()
            self.planeWidget[i].SetInteractor(self._iren)
            self.removeAllMouseEvents(self.planeWidget[i])
            
                        
                        
        self.resetBoxWidget()   
        self.resetAllPlaneWidgets()     
                
        self.create_color_opacity_table(tfuncdir + str(self.transferFunctionControlItems.combobox_transfunction.itemText(self.transferFunctionControlItems.combobox_transfunction.currentIndex())))
        
        for scale, idim, val in zip((self.scale_xmin,self.scale_ymin,self.scale_zmin,self.scale_xmax,self.scale_ymax,self.scale_zmax),(0,1,2,0,1,2),(0,0,0,self.dim[0],self.dim[1],self.dim[2])):
            scale.setMaximum(self.dim[idim])
            scale.setMinimum(0)
            scale.setValue(val)
            scale.setEnabled(True)
    
        for comp in (self.button_resetcrop, self.button_box):
            comp.setEnabled(True)
            
        for i in range(6):
            self.planeWidgetControlItems.button_pwidgets[i].setEnabled(True)
            self.planeWidgetControlItems.button_pwidgetreset[i].setEnabled(True)
            
        self.planeWidgetControlItems.button_pwdigetresetall.setEnabled(True)
            
        self.combobox_loadsettings.clear()            
        setting_files = glob.glob1(settings_dir+os.sep+self.sopuid, "*.xml")
        if setting_files:
            self.combobox_loadsettings.addItems(setting_files)  
            self.combobox_loadsettings.setCurrentIndex(self.combobox_loadsettings.findText("last-settings.xml"))
                        

        self.lightingControlItems.button_shade.setEnabled(True)
        self.lightingControlItems.button_interpolation.setEnabled(True)
        self.lightingControlItems.button_gradientopacity.setEnabled(True)
        
        for i in range(self.labelControlItems.combobox_labels.count()):
            self.labelLineRep[i].SetPoint1WorldPosition(self.reader.GetOutput().GetCenter())
            self.labelLineRep[i].SetPoint2WorldPosition(self.reader.GetOutput().GetOrigin())
        
        self.labelControlItems.button_label.setChecked(False)
                            
        self.smoothVolume()
        self.volumeMapper.CroppingOff()                
        self._ren.ResetCamera()     
        self._ren.ResetCameraClippingRange()   
        
        self.initStylus()     
        
        self.distanceWidget.GetDistanceRepresentation().SetPoint1WorldPosition(np.array([0,0,-100]))
        self.distanceWidget.GetDistanceRepresentation().SetPoint2WorldPosition(np.array([0,0,-200])) 
                      
        
        headtrack = vtkTimerHeadTrack(self.cam, self.headtracktext, self.stylustext, self.stylusactor, self.volume, self)
        headtrack.renderer = self._ren
        self._iren.AddObserver('TimerEvent', headtrack.execute)
        self._iren.CreateRepeatingTimer(20)  
                 
        
        self._renWin.Render()  
                
    def create_color_opacity_table(self,fname):    
        tree = ET.parse(fname)
    
        colorFunc = vtk.vtkColorTransferFunction()
        scalaropacityFunc = vtk.vtkPiecewiseFunction()
        gradientopacityFunc = vtk.vtkPiecewiseFunction()    
        
        rgbbranch = tree.iter('RGBTransferFunction')
        rgbsubbranch = rgbbranch.next().iter('ColorTransferFunction')
        for elem in rgbsubbranch.next():
            rgbval = elem.get('Value').split(" ")
            colorFunc.AddRGBPoint(float(elem.get('X')), float(rgbval[0]), float(rgbval[1]), float(rgbval[2]), float(elem.get('MidPoint')), float(elem.get('Sharpness')))    
    
        scalaropacitybranch = tree.iter('ScalarOpacity')
        scalaropacitysubbranch = scalaropacitybranch.next().iter('PiecewiseFunction')
        for elem in scalaropacitysubbranch.next():
            scalaropacityFunc.AddPoint(float(elem.get('X')), float(elem.get('Value')), float(elem.get('MidPoint')), float(elem.get('Sharpness')))
    
        gradientopacitybranch = tree.iter('GradientOpacity')
        gradientopacitysubbranch = gradientopacitybranch.next().iter('PiecewiseFunction')
        for elem in gradientopacitysubbranch.next():
            gradientopacityFunc.AddPoint(float(elem.get('X')), float(elem.get('Value')), float(elem.get('MidPoint')), float(elem.get('Sharpness')))
    
        volumeProp = tree.iter("VolumeProperty").next()
        component = tree.iter('Component').next()
        
        self.volumeProperty.SetSpecularPower(float(component.get('SpecularPower')))
        self.volumeProperty.SetDisableGradientOpacity(int(component.get('DisableGradientOpacity')))
        self.volumeProperty.SetScalarOpacityUnitDistance(float(component.get('ScalarOpacityUnitDistance')))
        self.volumeProperty.SetScalarOpacity(scalaropacityFunc)
        self.volumeProperty.SetColor(colorFunc)
        self.volumeProperty.SetGradientOpacity(gradientopacityFunc)    
        
        self.lightingControlItems.slider_ambient.setValue(100*float(component.get('Ambient')))  
        self.lightingControlItems.slider_diffuse.setValue(100*float(component.get('Diffuse')))
        self.lightingControlItems.slider_specular.setValue(100*float(component.get('Specular')))
        self.lightingControlItems.button_shade.setChecked(int(component.get('Shade')))
        self.lightingControlItems.button_interpolation.setChecked(int(volumeProp.get('InterpolationType')))
        
        self.adjustLights()
        self.setInterpolation()
        self.setShade()
        
    def setBoxWidget(self):
        if self.boxWidget.GetEnabled():
            self.boxWidget.Off()
        else:
            self.boxWidget.On()   
            
        self._renWin.Render() 
        
    def setPlaneWidgets(self):
        for i in range(6):
            if self.planeWidgetControlItems.button_pwidgets[i].isChecked():
                self.planeWidget[i].On()
                self.removeAllMouseEvents(self.planeWidget[i])
            else:
                self.planeWidget[i].Off()
            
                
    def updateTFunc(self):

        self.create_color_opacity_table(tfuncdir + str(self.transferFunctionControlItems.combobox_transfunction.itemText(self.transferFunctionControlItems.combobox_transfunction.currentIndex())))
        self._renWin.Render()

    def cropVolume(self):
        self.volumeMapper.SetCroppingRegionPlanes(self.scale_xmin.value()*self.spacing[0], self.scale_xmax.value()*self.spacing[0],\
                                                  self.scale_ymin.value()*self.spacing[1], self.scale_ymax.value()*self.spacing[1],\
                                                  self.scale_zmin.value()*self.spacing[2], self.scale_zmax.value()*self.spacing[2])
        self.volumeMapper.CroppingOn()
        self._renWin.Render()

    def resetCrop(self):
        for scale, val in zip((self.scale_xmin,self.scale_ymin,self.scale_zmin,self.scale_xmax,self.scale_ymax,self.scale_zmax),(0,0,0,self.dim[0],self.dim[1],self.dim[2])):
            scale.setValue(val)
        
        self.cropVolume()
        self.resetBoxWidget()
        self._renWin.Render()

    def setStereo(self):
        if self._renWin.GetStereoRender():
            self._renWin.StereoRenderOff()
        else:
            self._renWin.StereoRenderOn()
            
        self._renWin.Render()
        
    def setShade(self):
        if self.lightingControlItems.button_shade.isChecked():
            self.volumeProperty.ShadeOn()
            self.lightingControlItems.slider_ambient.setValue(100*self.volumeProperty.GetAmbient())
            self.lightingControlItems.slider_diffuse.setValue(100*self.volumeProperty.GetDiffuse())
            self.lightingControlItems.slider_specular.setValue(100*self.volumeProperty.GetSpecular())
            
            for comp in (self.lightingControlItems.slider_ambient, self.lightingControlItems.slider_diffuse, self.lightingControlItems.slider_specular, self.lightingControlItems.slider_keylightintensity):
                comp.setEnabled(True)
            
        else:
            self.volumeProperty.ShadeOff()
            
        self._renWin.Render()
        
    def setInterpolation(self):
        if self.lightingControlItems.button_interpolation.isChecked():
            self.volumeProperty.SetInterpolationTypeToLinear()
        else:
            self.volumeProperty.SetInterpolationTypeToNearest()
                        
        self._renWin.Render()
        
    def setDisableGradientOpacity(self):
        if self.lightingControlItems.button_gradientopacity.isChecked():
            self.volumeProperty.DisableGradientOpacityOn()
        else:
            self.volumeProperty.DisableGradientOpacityOff()
            
        self._renWin.Render()

    def setMeasurement(self):
        if self.distanceWidget.GetEnabled(): 
            self.distanceWidget.EnabledOff()
            self._ren.RemoveActor(self.distanceText) 
        else:
            self.distanceWidget.EnabledOn()
            self.removeAllMouseEvents(self.distanceWidget)
            self._ren.AddActor(self.distanceText) 
        
        self._renWin.Render()

    def setAngleMeasurement(self):
        if self.angleWidget.GetEnabled(): 
            self.angleWidget.EnabledOff()
            self._ren.RemoveActor(self.angleText) 
        else:
            self.angleWidget.EnabledOn()
            self._ren.AddActor(self.angleText) 
        
        self._renWin.Render()

    def saveSettings(self):
        
        if self.sopuid:
            self.pwClippingPlanes.GetMTime()
                
            root = ET.Element("root")    
            sliders = ET.SubElement(root, "sliders")
                
            for sldr, txt in zip((self.scale_xmin,self.scale_ymin,self.scale_zmin,self.scale_xmax,self.scale_ymax,self.scale_zmax),('x_min_slider', 'y_min_slider', 'z_min_slider', 'x_max_slider', 'y_max_slider', 'z_max_slider')):
                sliders.set(txt,str(sldr.value()))   
                
            bwtransform = vtk.vtkTransform()
            self.boxWidget.GetTransform(bwtransform)
            
            bwtransformsettings = ET.SubElement(root, "boxwidgettransform")
            buf = "" 
            for i in range(4):
                for j in range(4):
                    buf += str(bwtransform.GetMatrix().GetElement(i,j)) + ","
        
            bwtransformsettings.set("elements", buf[0:-1])
            bwtransformsettings.set("mtime", str(self.boxWidget.GetMTime()))
                  
            camera = ET.SubElement(root, "camera")
            camera.set("Position", str(self._ren.GetActiveCamera().GetPosition()))
            camera.set("FocalPoint", str(self._ren.GetActiveCamera().GetFocalPoint()))
            camera.set("ViewUp", str(self._ren.GetActiveCamera().GetViewUp()))
            
            planewidgetsettings = ET.SubElement(root, "planewidgetsettings")
            planewidgetsettings.set("mtime", str(self.pwClippingPlanes.GetMTime()))
            for i in range(6):
                planewidgetsettings.set("origin"+str(i), str(self.pwClippingPlanes.GetItem(i).GetOrigin()))
                planewidgetsettings.set("normal"+str(i), str(self.pwClippingPlanes.GetItem(i).GetNormal()))
            
            
            tfuncsettings = ET.SubElement(root, "tfunc")
            tfuncsettings.set("filename", str(self.transferFunctionControlItems.combobox_transfunction.itemText(self.transferFunctionControlItems.combobox_transfunction.currentIndex())))
            
            
            volPropSettings = ET.SubElement(root,'volumepropertysettings')
            rgbfuncsettings = ET.SubElement(volPropSettings,'rgbfuncsettings')
            rgbfuncsettings.set('NumberOfPoints',str(self.volumeProperty.GetRGBTransferFunction(0).GetSize()))
            val = np.empty((6))
            for i in range(self.volumeProperty.GetRGBTransferFunction(0).GetSize()):
                self.volumeProperty.GetRGBTransferFunction(0).GetNodeValue(i, val)
                rgbfuncsettings.set('pt'+str(i),"%d, %f, %f, %f, %f, %f" % (val[0],val[1],val[2],val[3],val[4],val[5]))
                
            scalarfuncsettings = ET.SubElement(volPropSettings,'scalarfuncsettings')        
            scalarfuncsettings.set('NumberOfPoints',str(self.volumeProperty.GetScalarOpacity(0).GetSize()))
            val = np.empty((4))
            for i in range(self.volumeProperty.GetScalarOpacity(0).GetSize()):    
                self.volumeProperty.GetScalarOpacity(0).GetNodeValue(i, val)
                scalarfuncsettings.set('pt'+str(i),"%d, %f, %f, %f" % (val[0],val[1],val[2],val[3]))
            
            gradientfuncsettings = ET.SubElement(volPropSettings,'gradientfuncsettings')        
            gradientfuncsettings.set('NumberOfPoints',str(self.volumeProperty.GetGradientOpacity(0).GetSize()))
            for i in range(self.volumeProperty.GetGradientOpacity(0).GetSize()):    
                self.volumeProperty.GetGradientOpacity(0).GetNodeValue(i, val)
                gradientfuncsettings.set('pt'+str(i),"%d, %f, %f, %f" % (val[0],val[1],val[2],val[3]))    
            
                   
            tree = ET.ElementTree(root)
            
            settings_subdir = self.sopuid            
            
            if not os.path.isdir(settings_dir):
                os.mkdir(settings_dir)
                
            if not os.path.isdir(settings_dir+os.sep+settings_subdir):
                os.mkdir(settings_dir+os.sep+settings_subdir)                
                
            if os.path.isfile(settings_dir + os.sep + settings_subdir+os.sep+"last-settings.xml"):
                os.rename(settings_dir + os.sep + settings_subdir+os.sep+"last-settings.xml", settings_dir + os.sep + settings_subdir+os.sep+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+".xml")
               
            
            options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
            filepath = QFileDialog.getSaveFileName(self,"Save Current Settings",settings_dir+ os.sep + settings_subdir+ os.sep + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),"XML Files (*.xml)", "XML Files (*.xml)",options)
                
            if filepath:
                _, ext = os.path.splitext(str(filepath))
                if ext.upper() != '.XML':
                    filepath = '%s.xml' % filepath

                tree.write(filepath)  

                filedir, fname = os.path.split(str(filepath))
            
                self.combobox_loadsettings.clear()            
                setting_files = glob.glob1(settings_dir+os.sep+self.sopuid, "*.xml")
                if setting_files:
                    self.combobox_loadsettings.addItems(setting_files)   
                    self.combobox_loadsettings.setCurrentIndex(self.combobox_loadsettings.findText(fname+".xml"))
        
    def loadSettings(self):
        if self.sopuid:
            fname = self.sopuid
            tree = None
            
            setting_fname = str(self.combobox_loadsettings.itemText(self.combobox_loadsettings.currentIndex()))
            
            if os.path.isfile(settings_dir + os.sep + fname+os.sep+setting_fname):
                tree = ET.parse(settings_dir + os.sep + fname+os.sep+setting_fname)  
            else:
                options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
                fname = QFileDialog.getOpenFileName(self,"Select Settings File",settings_dir,"All Files (*);;XML Files (*.xml)", "", options)
                if fname:
                    tree = ET.parse(fname)
            
            if tree:
                sliders = tree.iter('sliders').next()
             
                for sldr, txt in zip((self.scale_xmin,self.scale_ymin,self.scale_zmin,self.scale_xmax,self.scale_ymax,self.scale_zmax),('x_min_slider', 'y_min_slider', 'z_min_slider', 'x_max_slider', 'y_max_slider', 'z_max_slider')): 
                    sldr.setValue(int(sliders.get(txt)))
                    
                    
                bwtransformsettings = tree.iter('boxwidgettransform').next()                    
                tmatrix = np.fromstring(bwtransformsettings.get("elements"), sep=",")
                
                bwtransform = vtk.vtkTransform()
                bwmatrix = vtk.vtkMatrix4x4()
                for i in range(4):
                    for j in range(4):
                        bwmatrix.SetElement(i,j,tmatrix[4*i+j])
                     
                bwtransform.SetMatrix(bwmatrix)
                self.boxWidget.SetTransform(bwtransform)
                self.bwClipVolumeRender(self.boxWidget, None)
                
                
                if tree.findall('planewidgetsettings'):
                    planewidgetsettings = tree.iter('planewidgetsettings').next()
                    self.pwClippingPlanes.RemoveAllItems()
                    for i in range(6):
                        self.pwPlane[i].SetOrigin(np.fromstring(planewidgetsettings.get("origin"+str(i))[1:-1], sep=","))
                        self.pwPlane[i].SetNormal(np.fromstring(planewidgetsettings.get("normal"+str(i))[1:-1], sep=","))
                        self.pwClippingPlanes.AddItem(self.pwPlane[i])
                        self.planeWidget[i].SetOrigin(self.pwPlane[i].GetOrigin()[0],self.pwPlane[i].GetOrigin()[1],self.pwPlane[i].GetOrigin()[2])
                        self.planeWidget[i].SetNormal(self.pwPlane[i].GetNormal())
                        self.planeWidget[i].UpdatePlacement()                    
                    
                    if bwtransformsettings.get('mtime') and planewidgetsettings.get('mtime'):
                        bwtime = int(bwtransformsettings.get('mtime'))
                        pwtime = int(planewidgetsettings.get('mtime'))                                        
                        if pwtime > bwtime:
                            self.pwCallback(self, None)
                    

                camera = tree.iter('camera').next()
                self._ren.GetActiveCamera().SetPosition(np.fromstring(camera.get("Position")[1:-1], sep=","))
                self._ren.GetActiveCamera().SetFocalPoint(np.fromstring(camera.get("FocalPoint")[1:-1], sep=","))
                self._ren.GetActiveCamera().SetViewUp(np.fromstring(camera.get("ViewUp")[1:-1], sep=",")) 
                
                tfuncsetting = tree.iter("tfunc").next()
                self.transferFunctionControlItems.combobox_transfunction.setCurrentIndex(self.transferFunctionControlItems.combobox_transfunction.findText(tfuncsetting.get("filename")))
                self.create_color_opacity_table(tfuncdir + str(self.transferFunctionControlItems.combobox_transfunction.itemText(self.transferFunctionControlItems.combobox_transfunction.currentIndex())))
                
                rgbfunc = self.volumeProperty.GetRGBTransferFunction(0)
                rgbfunc.RemoveAllPoints()
                
                volumepropertysettings = tree.iter('volumepropertysettings').next()
                rgbfunctsettings = volumepropertysettings.iter('rgbfuncsettings').next()
                for i in range(int(rgbfunctsettings.get('NumberOfPoints'))):
                    val = np.fromstring(rgbfunctsettings.get('pt'+str(i)),sep=",")
                    rgbfunc.AddRGBPoint(val[0],val[1],val[2],val[3],val[4],val[5])
                    
                scalarfunc = self.volumeProperty.GetScalarOpacity(0)
                scalarfunc.RemoveAllPoints()            
        
                scalarfuncsettings = volumepropertysettings.iter('scalarfuncsettings').next()
                for i in range(int(scalarfuncsettings.get('NumberOfPoints'))):
                    val = np.fromstring(scalarfuncsettings.get('pt'+str(i)),sep=",")
                    scalarfunc.AddPoint(val[0],val[1],val[2],val[3])
                    
                gradientfunc = self.volumeProperty.GetGradientOpacity(0)
                gradientfunc.RemoveAllPoints()            
        
                gradientfuncsettings = volumepropertysettings.iter('gradientfuncsettings').next()
                for i in range(int(gradientfuncsettings.get('NumberOfPoints'))):
                    val = np.fromstring(gradientfuncsettings.get('pt'+str(i)),sep=",")
                    gradientfunc.AddPoint(val[0],val[1],val[2],val[3]) 
                    
                    
                       
            self.setShade()
            self._renWin.Render()

    def playCardiacCycle(self):
        if self.cb:
            if not self.isplay:
                self.isplay = True
                self.tag_observer1 = self._iren.AddObserver('TimerEvent', self.cb.execute)
                self._iren.CreateRepeatingTimer(10)
                self.cb.setplay(True)
            else:
                self.isplay = False
                self.cb.setplay(False)
                if not self.isrotate:
                    self._iren.RemoveObserver(self.tag_observer1)
    
    def rotateCamera(self):
        if self.cb:
            if not self.isrotate:
                self.isrotate = True
                self._iren.AddObserver('TimerEvent', self.cb.execute)
                self._iren.CreateRepeatingTimer(20)
                self.cb.setrotate(True)
            else:
                self.isrotate = False
                self.cb.setrotate(False)       
                if not self.isplay:
                    self._iren.RemoveObservers('TimerEvent')

    def editTransferFunction(self):
        if self.reader:
            self.transferFunctionEditor = TransferFunctionEditor(self.volumeProperty, self.reader, self._renWin)
            layout = pysideQGridLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.transferFunctionEditor.getTransferFunctionWidget())
             
            self.transferFunctionEditor.setLayout(layout)
            self.transferFunctionEditor.show()
                        
    def setStereoDepth(self, evt):
        self._ren.GetActiveCamera().SetEyeAngle(0.1*self.scale_stereodepth.value())
        self._renWin.Render()
        
    def setAzimuth(self, evt):
        val = self.scale_azimuth.value()
        self._ren.GetActiveCamera().Azimuth(self.varscaleazimuth-val)
        self.varscaleazimuth = val
        self._renWin.Render()
        
    def setElevation(self,evt):
        val = self.scale_elevation.value()
        self._ren.GetActiveCamera().Elevation(self.varscaleelevation-val)
        self.camerapos = self._ren.GetActiveCamera().OrthogonalizeViewUp() 
        self.varscaleelevation = val
        self._renWin.Render()

    def setRoll(self,evt):
        self._ren.GetActiveCamera().SetRoll(-1.0*self.scale_roll.value())
        self._renWin.Render()

    def zoomIn(self):
        self._ren.GetActiveCamera().Zoom(1.1)
        self._ren.ResetCameraClippingRange()
        self._renWin.Render()

    def zoomOut(self):
        self._ren.GetActiveCamera().Zoom(1.0/1.1)
        self._ren.ResetCameraClippingRange()
        self._renWin.Render()

    def resetCamera(self):
        self._ren.ResetCamera()
        self._ren.ResetCameraClippingRange()
        self._renWin.Render()
        
    def editOpacity(self):
        if self.reader:  
            self.opacityEditor = OpacityEditor(self.volumeProperty, self.reader, self._renWin)              
            self.opacityEditor.show()          

    def editGradientOpacity(self):
        if self.reader:                 
            self.opacityGradientEditor = GradientOpacityEditor(self.volumeProperty, self.reader, self._renWin)              
            self.opacityGradientEditor.show()   
    
    def editColor(self):
        if self.reader:     
            self.colorEditor = ColorEditor(self.volumeProperty, self.reader, self._renWin)
            self.colorEditor.show()
        
    def slider_imageNumber_valuechanged(self):
        if self.cb:
            self.label_imageNumber.setText(str(self.slider_imageNumber.value() + 1) + "/" + str(self.slider_imageNumber.maximum() + 1))    
            vol = self.volT[:, :, :, self.slider_imageNumber.value()]
            data_string = vol.flatten("A")
            self.reader.CopyImportVoidPointer(data_string, len(data_string)) 
            self.imageGaussianSmooth.Update()
            self._renWin.Render()    
            
    def smoothVolume(self):
        self.imageGaussianSmooth.SetStandardDeviations(0.1*self.slider_xsmooth.value(),0.1*self.slider_ysmooth.value(),0.1*self.slider_zsmooth.value())
        self.imageGaussianSmooth.Update()
        for label, slider in zip((self.label_xsmooth,self.label_ysmooth,self.label_zsmooth),(self.slider_xsmooth,self.slider_ysmooth,self.slider_zsmooth)):
            label.setText(str(slider.value()*0.1))   
            
        self._renWin.Render()
        
    def setNoSmooth(self):
        for slider in (self.slider_xsmooth,self.slider_ysmooth,self.slider_zsmooth):
            slider.setValue(0.0)
        
        self.smoothVolume()

    def setLowSmooth(self):
        for slider in (self.slider_xsmooth,self.slider_ysmooth,self.slider_zsmooth):
            slider.setValue(1)
        
        self.smoothVolume()
        
    def setMidSmooth(self):
        for slider in (self.slider_xsmooth,self.slider_ysmooth,self.slider_zsmooth):
            slider.setValue(10)
        
        self.smoothVolume()
        
    def setHighSmooth(self):
        for slider in (self.slider_xsmooth,self.slider_ysmooth,self.slider_zsmooth):
            slider.setValue(50)
        
        self.smoothVolume()                

    def adjustLights(self):
        
        self.lightingControlItems.label_ambient.setText('Ambient: %.2f' % (0.01*self.lightingControlItems.slider_ambient.value()))
        self.lightingControlItems.label_diffuse.setText('Diffuse: %.2f' % (0.01*self.lightingControlItems.slider_diffuse.value()))
        self.lightingControlItems.label_specular.setText('Specular: %.2f' % (0.01*self.lightingControlItems.slider_specular.value()))
                
        self.volumeProperty.SetAmbient(0.01*self.lightingControlItems.slider_ambient.value())
        self.volumeProperty.SetDiffuse(0.01*self.lightingControlItems.slider_diffuse.value())
        self.volumeProperty.SetSpecular(0.01*self.lightingControlItems.slider_specular.value())     
        
        self._renWin.Render()
        
    def setKeyLightIntensity(self):
        val = 0.2*self.lightingControlItems.slider_keylightintensity.value()
        
        self.lightingControlItems.label_keylightintensity.setText("Key Light Intensity: %.1f" % (val))
        
        self.lightkit.SetKeyLightIntensity(val)
        self._renWin.Render()
                
    def saveScreen(self):            
        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        filepath = QFileDialog.getSaveFileName(self,"Save Current Settings","","JPG Files (*.jpg)", "JPG Files (*.jpg)",options)
        if filepath:
            writer = vtk.vtkJPEGWriter()
            writer.SetFileName(str(filepath)+".jpg")
            writer.SetQuality(100)
            w2i = vtk.vtkWindowToImageFilter()
            w2i.SetInput(self._renWin)
            w2i.Update()
            writer.SetInputConnection(w2i.GetOutputPort())
            writer.Write()

    def changeView(self):
        str_button_view = self.sender().objectName()
        cam = self._ren.GetActiveCamera()
        focalpoint = cam.GetFocalPoint()
        dist = cam.GetDistance()
        
        
        

        if str_button_view == "button_view0":
            cam.SetPosition(focalpoint[0],focalpoint[1],focalpoint[2]+dist)
            cam.SetViewUp(0,1,0)
        if str_button_view == "button_view1":
            cam.SetPosition(focalpoint[0]+dist,focalpoint[1],focalpoint[2])
            cam.SetViewUp(0,1,0)
        if str_button_view == "button_view2":
            cam.SetPosition(focalpoint[0],focalpoint[1]+dist,focalpoint[2])
            cam.SetViewUp(0,0,-1)
        if str_button_view == "button_view3":
            cam.SetPosition(focalpoint[0],focalpoint[1],focalpoint[2]-dist)
            cam.SetViewUp(0,1,0)
        if str_button_view == "button_view4":
            cam.SetPosition(focalpoint[0]-dist,focalpoint[1],focalpoint[2])
            cam.SetViewUp(0,1,0)
        if str_button_view == "button_view5":
            cam.SetPosition(focalpoint[0],focalpoint[1]-dist,focalpoint[2])
            cam.SetViewUp(0,0,1)
        if str_button_view == "button_view6":
            self.scale_roll.setValue(0)
        if str_button_view == "button_view7":
            self.scale_roll.setValue(90)
        if str_button_view == "button_view8":
            self.scale_roll.setValue(180)
        if str_button_view == "button_view9":
            self.scale_roll.setValue(-90)
        
        self._renWin.Render()
         
    def displayLabel(self):
        i = self.labelControlItems.combobox_labels.currentIndex()        
        if self.labelControlItems.button_label.isChecked():
            self.labelActor[i].SetPosition(self.labelLineRep[i].GetPoint2WorldPosition())
            self.labelLine[i].EnabledOn()
            self._ren.AddActor(self.labelActor[i])
        else:
            self.labelLine[i].EnabledOff() 
            self._ren.RemoveActor(self.labelActor[i])
            
        self._renWin.Render()
        
    def changeLabelText(self):
        index = self.labelControlItems.combobox_labels.currentIndex()
        self.labelText[index].SetText(str(self.labelControlItems.text_label.text()))
        self._renWin.Render()
         
    def changeLabelSize(self):
        index = self.labelControlItems.combobox_labels.currentIndex()        
        self.labelActor[index].SetScale(0.1*self.labelControlItems.scale_labelsize.value())
        self._renWin.Render()
        
    def changeLabelIndex(self, value):
        self.labelControlItems.button_label.setChecked(self.labelLine[value].GetEnabled())
        self.labelControlItems.text_label.setText(self.labelText[value].GetText())
        
    def saveTransferFunction(self):
        
        root = ET.Element("TransferFunctions")          
        root.set("Type", "User")
        
        volumeProperty = ET.SubElement(root,"VolumeProperty")
        volumeProperty.set("InterpolationType", str(self.volumeProperty.GetInterpolationType()))
                
        component0 = ET.SubElement(volumeProperty, "Component")
        component0.set("Index", "0")
        component0.set("Shade", str(self.volumeProperty.GetShade(0)))
        component0.set("Ambient", str(self.volumeProperty.GetAmbient(0)))
        component0.set("Diffuse", str(self.volumeProperty.GetDiffuse(0)))
        component0.set("Specular", str(self.volumeProperty.GetSpecular(0)))
        component0.set("SpecularPower", str(self.volumeProperty.GetSpecularPower(0)))
        component0.set("DisableGradientOpacity", str(self.volumeProperty.GetDisableGradientOpacity(0)))
        component0.set("ComponentWeight", str(self.volumeProperty.GetComponentWeight(0)))
        component0.set("ScalarOpacityUnitDistance", str(self.volumeProperty.GetScalarOpacityUnitDistance(0)))
                                
        rgbtransferfuction = ET.SubElement(component0, "RGBTransferFunction")
        colorTransferFunction = ET.SubElement(rgbtransferfuction, "ColorTransferFunction")
        rgbfunction = self.volumeProperty.GetRGBTransferFunction(0)
        colorTransferFunction.set("Size",str(rgbfunction.GetSize()))
        
        nodeval = np.empty((6))
        for i in range(rgbfunction.GetSize()):
            rgbfunction.GetNodeValue(i, nodeval)
            point = ET.SubElement(colorTransferFunction, "Point")
            point.set("X",str(int(nodeval[0])))
            point.set("Value", "%f %f %f" % (nodeval[1], nodeval[2], nodeval[3]))
            point.set("MidPoint",str(int(nodeval[4])))
            point.set("Sharpness",str(int(nodeval[5])))

        scalarOpacity = ET.SubElement(component0, "ScalarOpacity")
        piecewiseFunction = ET.SubElement(scalarOpacity, "PiecewiseFunction")
        scalarfunction = self.volumeProperty.GetScalarOpacity(0)
        scalarOpacity.set("Size",str(scalarfunction.GetSize()))
        
        nodeval = np.empty((4))
        for i in range(scalarfunction.GetSize()):
            scalarfunction.GetNodeValue(i, nodeval)
            point = ET.SubElement(piecewiseFunction, "Point")
            point.set("X",str(int(nodeval[0])))
            point.set("Value", "%f" % nodeval[1])
            point.set("MidPoint",str(int(nodeval[2])))
            point.set("Sharpness",str(int(nodeval[3])))


        gradientOpacity = ET.SubElement(component0, "GradientOpacity")
        piecewiseFunction = ET.SubElement(gradientOpacity, "PiecewiseFunction")
        gradientfunction = self.volumeProperty.GetGradientOpacity(0)
        gradientOpacity.set("Size",str(gradientfunction.GetSize()))
        
        nodeval = np.empty((4))
        for i in range(gradientfunction.GetSize()):
            gradientfunction.GetNodeValue(i, nodeval)
            point = ET.SubElement(piecewiseFunction, "Point")
            point.set("X",str(int(nodeval[0])))
            point.set("Value", "%f" % nodeval[1])
            point.set("MidPoint",str(int(nodeval[2])))
            point.set("Sharpness",str(int(nodeval[3])))
                                
        
        tree = ET.ElementTree(root)        

        options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
        filepath = QFileDialog.getSaveFileName(self,"Save Transfer Function",tfuncdir+ os.sep + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),"VVT Files (*.vvt)", "VVT Files (*.vvt)",options)
        if filepath:
            _, ext = os.path.splitext(str(filepath))
            if ext.upper() != '.VVT':
                filepath = '%s.vvt' % filepath
       
        tree.write(filepath)
        
        
        filedir, fname = os.path.split(str(filepath))
        
        self.transferFunctionControlItems.combobox_transfunction.clear()
    
        tfunc_files = glob.glob1(tfuncdir,"*.vvt")
        if tfunc_files:
            self.transferFunctionControlItems.combobox_transfunction.addItems(tfunc_files)   
            self.transferFunctionControlItems.combobox_transfunction.setCurrentIndex(self.transferFunctionControlItems.combobox_transfunction.findText(fname+".vvt"))        
        
         
def main():        

    app = QApplication([])

    File = QFile("darkorange.stylesheet")
    File.open(QFile.ReadOnly)
    StyleSheet = QLatin1String(File.readAll())    
 
    app.setStyleSheet(StyleSheet)

    tdviz = TDVizCustom()
    tdviz.show()
    

    if isprojector:
        tdviz.setGeometry(1920, 0, 1280, 1024)
    else:
        tdviz.showFullScreen()    

    yscreenf = 1.0*tdviz._renWin.GetSize()[1]/1080.0

    cam = tdviz._ren.GetActiveCamera()
    cam.SetScreenBottomLeft(-262.5,148.5-148.5*2.0*yscreenf,-410)
    cam.SetScreenBottomRight(262.5,148.5-148.5*2.0*yscreenf,-410)
    cam.SetScreenTopRight(262.5,148.5,-410) 


    sys.exit(app.exec_())   
        
if __name__ == "__main__": 
     main()
