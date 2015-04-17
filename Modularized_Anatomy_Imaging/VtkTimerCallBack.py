'''
Created on Mar 10, 2015

Creates a timer for the vtk callback??
'''

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
