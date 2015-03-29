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
            
        '''
        self.plane = vtk.vtkPlane()
        self.plane.SetOrigin(0,0,0) #Add arguments
        self.plane.SetNormal(0,0,0) #Add arguments
        self.plane.UpdatePlacement() 
        '''
        self.planeWidget = vtk.vtkImplicitPlaneWidget()
        #self.planeWidget.SetInteractor(self._iren)
        #self.planeWidget.SetPlaceFactor(1.1)
        #self.planeWidget.TubingOff()
        #self.planeWidget.DrawPlaneOff()
        #self.planeWidget.OutsideBoundsOff()  
        #self.planeWidget.OutlineTranslationOff() 
        #self.planeWidget.ScaleEnabledOff()
        #self.planeWidget.SetHandleSize(0.25*self.planeWidget.GetHandleSize())
        #self.planeWidget.SetKeyPressActivationValue(str(1))
        #self.planeWidget.SetInteractor(self._iren)
        #self.planeWidget.AddObserver("InteractionEvent", self.pwCallback)  
                
        
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
        self.planeWidget.PlaceWidget(-2*x,x*2,-2*y,y*2,-2*z,z*2) # @UndefinedVariable
        #self.planeWidget.SetOrigin(x*2,y*2,z*2)
        #self.planeWidget.SetNormal(1,0,0)
        self.planeWidget.UpdatePlacement()
        self.planeWidget.On()
        
        
def init():
    global planeGenerator
    planeGenerator = PlaneGenerator() 
    
def getPlane():
    return planeGenerator
    #return planeGenerator.getCubeActor()

def setPlanePosition(self,x,y,z):
        planeGenerator.setPosition(x,y,z)