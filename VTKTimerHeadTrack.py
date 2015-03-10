'''
Created on Mar 10, 2015

@author: Bradley
'''

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
        