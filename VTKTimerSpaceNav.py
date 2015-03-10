'''
Created on Mar 10, 2015

@author: Bradley
'''

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

