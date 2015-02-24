import vtk
import vrpn
import time
from trace import threading
from threading import Thread
import numpy as np
import math

print vtk.VTK_VERSION

def callback(userdata, data):
    print userdata, "=>", data
    
    
camMatrix = np.array([1.000000, 0.000000, 0.000000, 0.000000, 0.000000, 0.541127, -0.840941, 0.000000, 0.000000, 0.840941, 0.541127, 0.000000, 0.000000, 0.000000, 0.000000, 1.000000])
camMat4x4 = np.reshape(camMatrix, (4,4))
   
class vtkTimerCallBack():
    tracker=vrpn.receiver.Tracker("Tracker0@localhost")
    button=vrpn.receiver.Button("Tracker0@localhost")

    def __init__(self, camera, textCamPos, textStylus, lineactor):
        self.textCamPos = textCamPos
        self.textStylus = textStylus
        self.tracker.register_change_handler("tracker", self.callback, "position")
        self.button.register_change_handler("button", self.callback_button)
        
        self.lineactor = lineactor
        
        self.camera = camera
        self.rmatrix = np.zeros((4,4))
        self.rmatrix4x4 = vtk.vtkMatrix4x4()   
                
        self.button0state = False
        self.button1state = False
        self.button2state = False

            
        self.initialZPosition = None
        self.initialScaleTransform = None
        
        self.initialCameraUserViewTransform = None
        
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
            self.textCamPos.SetInput("pos = (%-#6.3g, %-#6.3g, %-#6.3g)\n quaternion = (%-#6.3g, %-#6.3g, %-#6.3g, %-#6.3g)" % (dx, dy, dz, qw, qx, qy, qz))
    
            if not math.isnan(dx) and not math.isnan(qx):
                self.camera.SetEyeTransformMatrix(self.rmatrix.reshape(16,1))
                
                
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
                  
                self.camera.SetUserViewTransform(stylusTransform)
                self.camera.ViewingRaysModified()
                self.camera.Modified()
                
                
            else:
                self.initialCameraTransformMatrix = transformCam
                self.initialCameraUserViewTransform = self.camera.GetUserViewTransform()
 
                modeltransform = vtk.vtkTransform()
                modeltransform.Concatenate(self.camera.GetModelViewTransformMatrix())
               
                transform.Concatenate(modeltransform.GetInverse())                           
                self.lineactor.SetUserTransform(transform)                
                self.lineactor.Modified()   
                
            if self.button1state:
                if self.initialZPosition:
                    scaleTransform = vtk.vtkTransform()
                    scale = (1 + 10*(dz - self.initialZPosition))
                    
                    if self.initialScaleTransform:
                        scaleTransform.Concatenate(self.initialScaleTransform)

                    scaleTransform.Scale(scale, scale, scale)
                        
                    self.camera.SetUserViewTransform(scaleTransform)
                    self.camera.Modified()                        

            else:
                self.initialZPosition = dz
                self.initialScaleTransform = self.camera.GetUserViewTransform()
               
            self.textStylus.SetInput("pos = (%-#6.3g, %-#6.3g, %-#6.3g)\n quaternion = (%-#6.3g, %-#6.3g, %-#6.3g, %-#6.3g)" % (self.rmatrix4x4.GetElement(0, 3), self.rmatrix4x4.GetElement(1, 3), self.rmatrix4x4.GetElement(2, 3), qw, qx, qy, qz))
                
    def getCamera(self):
        return self.camera
    
    def getSpeedFactor(self):
        pos = self.camera.GetPosition()
        foc = self.camera.GetFocalPoint()
        
        v_pos = np.array([pos[0] - foc[0], pos[1]-foc[1], pos[2]-foc[2]])
        
        return np.linalg.norm(v_pos)
   
   

def main():
    
    cube = vtk.vtkCubeSource()
    cube.SetXLength(60)
    cube.SetYLength(60)
    cube.SetZLength(60)
    
    cubeMapper = vtk.vtkPolyDataMapper()
    cubeMapper.SetInputConnection(cube.GetOutputPort())
    
    cubeActor = vtk.vtkActor()
    cubeActor.SetMapper(cubeMapper)
    cubeActor.GetProperty().SetColor(0.2, 0.6, 0.8)
    cubeActor.SetPosition(-30, -30, -150)

    sphere = vtk.vtkSphereSource()
    sphere.SetThetaResolution(30)
    sphere.SetPhiResolution(30)
    sphere.SetRadius(2)
    
    sphereTransform = vtk.vtkTransform()
    sphereTransform.Translate(0, 0, -100)

    sphereMapper = vtk.vtkPolyDataMapper()
    sphereMapper.SetInputConnection(sphere.GetOutputPort())
    
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
    
    lineActor = vtk.vtkActor()
    lineActor.SetMapper(lineMapper)    
    
    ren = vtk.vtkRenderer()
    ren.AddActor(lineActor)
    
    
    axes = vtk.vtkAxesActor()
    axesWidget = vtk.vtkOrientationMarkerWidget()
    axes.AxisLabelsOff()
    axes.SetShaftTypeToCylinder()
    
    ren.AddActor(cubeActor)
    ren.SetBackground(0.15, 0.15, 0.15)
    
    lightkit = vtk.vtkLightKit()
    lightkit.AddLightsToRenderer(ren)
    
    renWin = vtk.vtkRenderWindow()
    renWin.SetStereoCapableWindow(1)
    renWin.SetStereoTypeToCrystalEyes()
    renWin.SetStereoRender(1)
    
    
    renWin.AddRenderer(ren)
    renWin.SetFullScreen(True)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

    renWin.Render()
    
    yscreenf = 1.0*renWin.GetSize()[1]/1080.0
    
    camera = ren.GetActiveCamera()    
    camera.SetScreenBottomLeft(-262.5,148.5-148.5*2.0*yscreenf,-410)
    camera.SetScreenBottomRight(262.5,148.5-148.5*2.0*yscreenf,-410)
    camera.SetScreenTopRight(262.5,148.5,-410)    
    camera.SetUseOffAxisProjection(1)
    camera.SetEyeSeparation(60)
   
    axesWidget.SetOrientationMarker(axes)
    axesWidget.SetInteractor(iren)
    axesWidget.SetViewport(0.0, 0.0, 0.3, 0.3)
    axesWidget.SetEnabled(1)
    axesWidget.InteractiveOff()   
    
    
    textCamPos = vtk.vtkTextActor()        
    textCamPos.SetDisplayPosition(20, 20)      
    textCamPos.SetInput("0")
    ren.AddActor(textCamPos) 
     
    textStylus = vtk.vtkTextActor()        
    textStylus.SetDisplayPosition(1600, 20)      
    textStylus.SetInput("0")
    ren.AddActor(textStylus)     
       
    iren.Initialize()

    cb = vtkTimerCallBack(camera, textCamPos, textStylus, lineActor)
    cb.renderer = ren
    iren.AddObserver('TimerEvent', cb.execute)
    iren.CreateRepeatingTimer(10)
        
    renWin.Render()
      
    iren.Start()
        
if __name__ == '__main__':
    main()
