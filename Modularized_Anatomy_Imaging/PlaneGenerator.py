import vtk
import GlobalVariables
'''
Created on Mar 12, 2015

@author: ANATOMY-IMAGING
'''

class PlaneGenerator(object):
    '''
    classdocs
    '''

    def __init__(self):
            
        
        self.plane = vtk.vtkPlane()
        self.plane.SetOrigin(0,0,0)
        self.plane.SetNormal(0,0,0) 
        #self.plane.UpdatePlacement() 
        
        
        self.x = GlobalVariables.imageXDist/2.0 # @UndefinedVariable
        self.y = GlobalVariables.imageYDist/2.0 # @UndefinedVariable
        self.z = GlobalVariables.imageZDist/2.0 # @UndefinedVariable
        
        self.planeWidget = vtk.vtkImplicitPlaneWidget()
        #self.planeWidget.SetPlaceFactor(1.1)
        self.planeWidget.TubingOff()
        #self.planeWidget.DrawPlaneOff()
        #self.planeWidget.OutsideBoundsOff()  
        self.planeWidget.OutlineTranslationOff() 
        self.planeWidget.ScaleEnabledOff()
        #self.planeWidget.HandlesOff()
        self.planeWidget.SetHandleSize(0.25*self.planeWidget.GetHandleSize())
        #self.planeWidget.SetKeyPressActivationValue(str(1))
        #self.planeWidget.AddObserver("InteractionEvent", self.pwCallback)
        
        #create cutter
        self.cutter=vtk.vtkCutter()
        self.cutter.SetCutFunction(self.planeWidget.GetPlane(self.plane))
        #cutter.SetInputConnection(cube.GetOutputPort())
        self.cutter.Update()
        self.cutterMapper=vtk.vtkPolyDataMapper()
        #self.cutterMapper.SetInputConnection(self.cutter.GetOutputPort())
        
        #create plane actor
        self.planeActor=vtk.vtkActor()
        self.planeActor.GetProperty().SetColor(1.0,1,0)
        self.planeActor.GetProperty().SetLineWidth(2)
        self.planeActor.SetMapper(self.cutterMapper)
        self.planeActor.SetPosition(self.x,self.y,self.z)
        
        
        '''
        cube = vtk.vtkCubeSource()
        cube.SetXLength(120)
        cube.SetYLength(120)
        cube.SetZLength(0)

        #cubeTransform = vtk.vtkTransform()
        #cubeTransform.Translate(0, 0, 0)
        
        cubeMapper = vtk.vtkPolyDataMapper()
        cubeMapper.SetInputConnection(cube.GetOutputPort())
                
        cubeTransformFilter = vtk.vtkTransformPolyDataFilter()
        cubeTransformFilter.SetInputConnection(cube.GetOutputPort())
        #cubeTransformFilter.SetTransform(cubeTransform)
        
        appendFilter = vtk.vtkAppendPolyData()
        #appendFilter.AddInputConnection(line.GetOutputPort())
        appendFilter.AddInputConnection(cubeTransformFilter.GetOutputPort())
       
        self.x = GlobalVariables.imageXDist/2.0 # @UndefinedVariable
        self.y = GlobalVariables.imageYDist/2.0 # @UndefinedVariable
        self.z = GlobalVariables.imageZDist/2.0 # @UndefinedVariable
        
        self.cubeActor = vtk.vtkActor()
        self.cubeActor.SetMapper(cubeMapper)
        self.cubeActor.GetProperty().SetColor(0.2, 0.6, 0.8)
        self.cubeActor.SetPosition(self.x,self.y,self.z)#(self.sampleSpacing[0]/2,self.sampleSpacing[1]/2,self.sampleSpacing[2]/2)#(-30, -30, -150) #(70,90,50)
        '''
        
    def setPlaneInteractor(self, interactor):
        self.planeWidget.SetInteractor(interactor) 
        self.planeWidget.UpdatePlacement() 

    def getPlane(self):
        return self.planeWidget
        #return self.cubeActor
    
    def setPlanePosition(self,x,y,z):
        self.planeWidget.PlaceWidget(-2*x,x*4,-2*y,y*4,-2*z,z*4) # @UndefinedVariable
        #self.planeWidget.SetOrigin(x*2,y*2,z*2)
        #self.planeWidget.SetNormal(0,0,0)
        #self.planeWidget.UpdatePlacement()
        self.planeWidget.On()
        
    def getPlaneActor(self):
        return self.planeActor
        
        
def init():
    global planeGenerator
    planeGenerator = PlaneGenerator() 
    
def getPlane():
    return planeGenerator
    #return planeGenerator.getCubeActor()

def setPlanePosition(self,x,y,z):
        planeGenerator.setPosition(x,y,z)