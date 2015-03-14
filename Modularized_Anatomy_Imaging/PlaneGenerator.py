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

    def getCubeActor(self):
        return self.cubeActor
    
    def setCubeActorPosition(self,x,y,z):
        self.cubeActor.setPosition(x,y,z)
        
def init():
    global planeGenerator
    planeGenerator = PlaneGenerator() 
    
def getCubeActor():
    return planeGenerator.getCubeActor()

def setCubeActorPosition(self,x,y,z):
        planeGenerator.cubeActor.setPosition(x,y,z)