from PyQt4.QtGui import QApplication, QMainWindow, QFrame, QGridLayout, QWidget, QScrollBar, QLabel, QTabWidget, QPushButton, QHBoxLayout, QSpinBox, QFileDialog, QComboBox, QGroupBox, QVBoxLayout, QDial, QDialog, QSlider, QMenu, QLineEdit
from PyQt4.QtCore import Qt, QFile, QLatin1String, QSize
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk, sys, dicom, numpy as np, glob, xml.etree.ElementTree as ET, os, datetime, colorsys
from ui.widgets.transferfunction import TransferFunction, TransferFunctionWidget
from PySide.QtGui import QDialog as pysideQWidget
from PySide.QtGui import QGridLayout as pysideQGridLayout
import vrpn
import math
import GlobalVariables
import CropControlItems, CommonControlItems, PositionControlItems, TransferFunctionControlItems, PlaneWidgetControlItems, PlayControlItems
import SmoothingControlItems, LightingControlItems, ViewControlItems, LabelControlItems, VtkTimerCallBack, VTKTimerHeadTrack, TransferFunctionEditor
import OpacityEditor, GradientOpacityEditor, ColorEditor

'''
Created on Mar 10, 2015

TODO: Fix GlobalVariables references
TODO: Find out the difference between this and TDVizCustom

@author: Bradley
'''

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
        
        
'''
Created on Mar 10, 2015

@author: Bradley
'''

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
        
        tfuncs = glob.glob1(GlobalVariables.tfuncdir, "*.vvt")
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
        self.fname = QFileDialog.getOpenFileName(self,"Select DICOM File",GlobalVariables.initfdir,"All Files (*);;Text Files (*.txt)", "", options)        
        
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
            self.cb = VtkTimerCallBack.vtkTimerCallBack(self.volT.shape[3], self.isplay, self.isrotate, self.slider_imageNumber)
            
            self.cb.renderer = self._ren
    
    def loadDir(self):
        options = QFileDialog.DontResolveSymlinks | QFileDialog.ShowDirsOnly | QFileDialog.DontUseNativeDialog
        self.dirname = str(QFileDialog.getExistingDirectory(self,"Select DICOM Directory", GlobalVariables.initddir, options))
        
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
                
        self.create_color_opacity_table(GlobalVariables.tfuncdir + str(self.transferFunctionControlItems.combobox_transfunction.itemText(self.transferFunctionControlItems.combobox_transfunction.currentIndex())))
        
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
        setting_files = glob.glob1(GlobalVariables.settings_dir+os.sep+self.sopuid, "*.xml")
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
                      
        
        headtrack = VTKTimerHeadTrack.vtkTimerHeadTrack(self.cam, self.headtracktext, self.stylustext, self.stylusactor, self.volume, self)
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

        self.create_color_opacity_table(GlobalVariables.tfuncdir + str(self.transferFunctionControlItems.combobox_transfunction.itemText(self.transferFunctionControlItems.combobox_transfunction.currentIndex())))
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
            
            if not os.path.isdir(GlobalVariables.settings_dir):
                os.mkdir(GlobalVariables.settings_dir)
                
            if not os.path.isdir(GlobalVariables.settings_dir+os.sep+settings_subdir):
                os.mkdir(GlobalVariables.settings_dir+os.sep+settings_subdir)                
                
            if os.path.isfile(GlobalVariables.settings_dir + os.sep + settings_subdir+os.sep+"last-settings.xml"):
                os.rename(GlobalVariables.settings_dir + os.sep + settings_subdir+os.sep+"last-settings.xml", settings_dir + os.sep + settings_subdir+os.sep+datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")+".xml")
               
            
            options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
            filepath = QFileDialog.getSaveFileName(self,"Save Current Settings",settings_dir+ os.sep + settings_subdir+ os.sep + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),"XML Files (*.xml)", "XML Files (*.xml)",options)
                
            if filepath:
                _, ext = os.path.splitext(str(filepath))
                if ext.upper() != '.XML':
                    filepath = '%s.xml' % filepath

                tree.write(filepath)  

                filedir, fname = os.path.split(str(filepath))
            
                self.combobox_loadsettings.clear()            
                setting_files = glob.glob1(GlobalVariables.settings_dir+os.sep+self.sopuid, "*.xml")
                if setting_files:
                    self.combobox_loadsettings.addItems(setting_files)   
                    self.combobox_loadsettings.setCurrentIndex(self.combobox_loadsettings.findText(fname+".xml"))
        
    def loadSettings(self):
        if self.sopuid:
            fname = self.sopuid
            tree = None
            
            setting_fname = str(self.combobox_loadsettings.itemText(self.combobox_loadsettings.currentIndex()))
            
            if os.path.isfile(GlobalVariables.settings_dir + os.sep + fname+os.sep+setting_fname):
                tree = ET.parse(GlobalVariables.settings_dir + os.sep + fname+os.sep+setting_fname)  
            else:
                options = QFileDialog.Options() | QFileDialog.DontUseNativeDialog
                fname = QFileDialog.getOpenFileName(self,"Select Settings File",GlobalVariables.settings_dir,"All Files (*);;XML Files (*.xml)", "", options)
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
                self.create_color_opacity_table(GlobalVariables.tfuncdir + str(self.transferFunctionControlItems.combobox_transfunction.itemText(self.transferFunctionControlItems.combobox_transfunction.currentIndex())))
                
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
            self.transferFunctionEditor = TransferFunctionEditor.TransferFunctionEditor(self.volumeProperty, self.reader, self._renWin)
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
            self.opacityEditor = OpacityEditor.OpacityEditor(self.volumeProperty, self.reader, self._renWin)              
            self.opacityEditor.show()          

    def editGradientOpacity(self):
        if self.reader:                 
            self.opacityGradientEditor = GradientOpacityEditor.GradientOpacityEditor(self.volumeProperty, self.reader, self._renWin)              
            self.opacityGradientEditor.show()   
    
    def editColor(self):
        if self.reader:     
            self.colorEditor = ColorEditor.ColorEditor(self.volumeProperty, self.reader, self._renWin)
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
        filepath = QFileDialog.getSaveFileName(self,"Save Transfer Function",GlobalVariables.tfuncdir+ os.sep + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),"VVT Files (*.vvt)", "VVT Files (*.vvt)",options)
        if filepath:
            _, ext = os.path.splitext(str(filepath))
            if ext.upper() != '.VVT':
                filepath = '%s.vvt' % filepath
       
        tree.write(filepath)
        
        
        filedir, fname = os.path.split(str(filepath))
        
        self.transferFunctionControlItems.combobox_transfunction.clear()
    
        tfunc_files = glob.glob1(GlobalVariables.tfuncdir,"*.vvt")
        if tfunc_files:
            self.transferFunctionControlItems.combobox_transfunction.addItems(tfunc_files)   
            self.transferFunctionControlItems.combobox_transfunction.setCurrentIndex(self.transferFunctionControlItems.combobox_transfunction.findText(fname+".vvt"))        
