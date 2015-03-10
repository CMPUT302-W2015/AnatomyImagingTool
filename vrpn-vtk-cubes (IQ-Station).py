import vtk
import vrpn
import time
import numpy as np
import math

print vtk.VTK_VERSION

def callback(userdata, data):
    print userdata, "=>", data


    
class vtkTimerCallBack():
    tracker=vrpn.receiver.Tracker("head@localhost:3883")
    
    def __init__(self, ren, text):
        self.ren = ren
        self.text = text
        self.tracker.register_change_handler("tracker", self.callback, "position")
        self.cam = self.ren.GetActiveCamera()
        self.rmatrix = np.zeros((4,4))

        for i in range(3):
            self.rmatrix[i,i] = 1.0

        
    def execute(self, obj, event):
        iren = obj
        self.tracker.mainloop()
            
        iren.GetRenderWindow().Render()    
    
    def callback(self, userdata, data):
        dx, dy, dz = data['position']
        qx, qy, qz, qw = data['quaternion']

        self.text.SetInput("pos = (%-#6.3g, %-#6.3g, %-#6.3g)\n quaternion = (%-#6.3g, %-#6.3g, %-#6.3g, %-#6.3g)" % (dx, dy, dz, qw, qx, qy, qz))

        
        if not math.isnan(dx) and not math.isnan(qx):
            qwxyz = np.array([qw,qx,qy,qz])
            
            vtk.vtkMath.QuaternionToMatrix3x3(qwxyz, self.rmatrix[0:3,0:3])            
            self.rmatrix[3,3] = 1.0                        
            self.cam.SetEyeTransformMatrix(self.rmatrix.reshape(16,1))
            self.cam.SetEyePosition([1000*dx, 1000*dy, 1000*dz])

        

def main():
    cube = vtk.vtkCubeSource()
    cube.SetXLength(100)
    cube.SetYLength(100)
    cube.SetZLength(100)
    
    cubeMapper = vtk.vtkPolyDataMapper()
    cubeMapper.SetInputConnection(cube.GetOutputPort())
    
    cubeActor = vtk.vtkActor()
    cubeActor.SetMapper(cubeMapper)
    cubeActor.GetProperty().SetColor(0.2, 0.63, 0.79)
    cubeActor.GetProperty().SetDiffuse(0.7)
    cubeActor.GetProperty().SetSpecular(0.4)
    cubeActor.GetProperty().SetSpecularPower(20)
    cubeActor.GetProperty().SetInterpolationToPhong()
    cubeActor.GetProperty().ShadingOn()
    cubeActor.SetPosition(0, 0, 600)
    
    property = vtk.vtkProperty()
    property.SetColor(1.0, 0.3882, 0.2784)
    property.SetDiffuse(0.7)
    property.SetSpecular(0.4)
    property.SetSpecularPower(20)
    
    cubeActor2 = vtk.vtkActor()
    cubeActor2.SetMapper(cubeMapper)
    cubeActor2.GetProperty().SetColor(0.2, 0.63, 0.79)
    cubeActor2.SetProperty(property)
    cubeActor2.SetPosition(0, 0, 300)
    
    ren1 = vtk.vtkRenderer()
    ren1.AddActor(cubeActor)
    
    
    axes = vtk.vtkAxesActor()
    axesWidget = vtk.vtkOrientationMarkerWidget()
    axes.AxisLabelsOff()
    axes.SetShaftTypeToCylinder()
    
    
    ren1.AddActor(cubeActor2)
    ren1.SetBackground(0.1, 0.2, 0.4)
    
    lightkit = vtk.vtkLightKit()
    lightkit.AddLightsToRenderer(ren1)
    
    renWin = vtk.vtkRenderWindow()
    renWin.SetStereoCapableWindow(1)
    renWin.SetStereoTypeToCrystalEyes()
    renWin.SetStereoRender(1)
    
    
    renWin.AddRenderer(ren1)
    renWin.SetSize(1920, 1080)
    renWin.SetBorders(0)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.SetInteractorStyle(vtk.vtkInteractorStyleTrackballCamera())

    renWin.Render()
    
    
    cam = ren1.GetActiveCamera()
    cam.UseOffAxisProjectionOn()

    cam.SetScreenBottomLeft(-717,-403,-1000)
    cam.SetScreenBottomRight(717,-403,-1000)
    cam.SetScreenTopRight(717,403,-1000)
    cam.SetEyeSeparation(65)

    
    axesWidget.SetOrientationMarker(axes)
    axesWidget.SetInteractor(iren)
    axesWidget.SetViewport(0.0, 0.0, 0.3, 0.3)
    axesWidget.SetEnabled(1)
    axesWidget.InteractiveOff()   
    
    
    text = vtk.vtkTextActor()        
    text.SetTextScaleModeToProp()
    text.SetDisplayPosition(20, 20)      
    text.SetInput("")
    ren1.AddActor(text) 
    
    
    cb = vtkTimerCallBack(ren1,text)
    cb.renderer = ren1
    iren.AddObserver('TimerEvent', cb.execute)
    iren.CreateRepeatingTimer(30)
        

    iren.Start()
    
if __name__ == '__main__':
    main()