import vtk
'''
Created on Mar 12, 2015

@author: ANATOMY-IMAGING
'''
class PlaneGenerator(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        cube = vtk.vtkCubeSource()
        cube.SetXLength(60)
        cube.SetYLength(60)
        cube.SetZLength(0)
    
        cubeMapper = vtk.vtkPolyDataMapper()
        cubeMapper.SetInputConnection(cube.GetOutputPort())
        
        cubeActor = vtk.vtkActor()
        cubeActor.SetMapper(cubeMapper)
        cubeActor.GetProperty().SetColor(0.2, 0.6, 0.8)
        cubeActor.SetPosition(-30, -30, -150)
    
        
        ren = vtk.vtkRenderer()
    
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
    
        #cb = vtkTimerCallBack(camera, textCamPos, textStylus)
        #cb.renderer = ren
        #iren.AddObserver('TimerEvent', cb.execute)
        #iren.CreateRepeatingTimer(10)
            
        renWin.Render()
          
        iren.Start()
        


if __name__ == "__main__":
    c = PlaneGenerator()
    

        