'''
Created on Mar 10, 2015

@author: Bradley
'''

class TransferFunctionEditor(pysideQWidget): 
    def __init__(self, volumeProperty, reader, renWin):        
        super(TransferFunctionEditor, self).__init__()    
        self.volumeProperty = volumeProperty
        self.reader = reader
        self._renderWindow = renWin
        self.setWindowTitle("Transfer Function Editor") 
        
        self.opacityfunction =  self.volumeProperty.GetScalarOpacity(0)
        self.colorfunction =  self.volumeProperty.GetRGBTransferFunction(0)

        self.npts = self.opacityfunction.GetSize()
        
        imageData = reader.GetOutput()
        self.histogramWidget = TransferFunctionWidget()
        transferFunction = TransferFunction()
        
        rmax = self.reader.GetOutput().GetScalarRange()[1] 
        rmin = self.reader.GetOutput().GetScalarRange()[0]         
        transferFunction.setRange([rmin, rmax])
        
        self.minimum, self.maximum = rmin, rmax
        
        opacityNode = np.empty((4,))
        transferFunction.addPoint(rmin, self.opacityfunction.GetValue(rmin), color=[self.colorfunction.GetRedValue(rmin), self.colorfunction.GetGreenValue(rmin), self.colorfunction.GetBlueValue(rmin)])
        for i in range(self.npts):
            self.opacityfunction.GetNodeValue(i, opacityNode)
            if (opacityNode[0] > rmin) and (opacityNode[0] < rmax):
                transferFunction.addPoint(opacityNode[0], opacityNode[1], color=[self.colorfunction.GetRedValue(opacityNode[0]), self.colorfunction.GetGreenValue(opacityNode[0]), self.colorfunction.GetBlueValue(opacityNode[0])])       
            
        transferFunction.addPoint(rmax, self.opacityfunction.GetValue(rmax), color=[self.colorfunction.GetRedValue(rmax), self.colorfunction.GetGreenValue(rmax), self.colorfunction.GetBlueValue(rmax)])
        
        transferFunction.updateTransferFunction() 
        
        self.histogramWidget.transferFunction = transferFunction 
        self.histogramWidget.setImageData(imageData)        
        self.histogramWidget.transferFunction.updateTransferFunction()        
        self.histogramWidget.updateNodes()  
        
        self.histogramWidget.valueChanged.connect(self.valueChanged)

        self.resize(400,300)
        
    def getTransferFunctionWidget(self):
        return self.histogramWidget        
    
    def updateTransferFunction(self):
        if self.histogramWidget:
            self.histogramWidget.transferFunction.updateTransferFunction()
            self.colorFunction = self.histogramWidget.transferFunction.colorFunction
            self.opacityFunction = self.histogramWidget.transferFunction.opacityFunction
        else:
            # Transfer functions and properties
            self.colorFunction = vtkColorTransferFunction()
            self.colorFunction.AddRGBPoint(self.minimum, 0, 0, 0)
            self.colorFunction.AddRGBPoint(self.maximum, 0, 0, 0)

            self.opacityFunction = vtkPiecewiseFunction()
            self.opacityFunction.AddPoint(self.minimum, 0)
            self.opacityFunction.AddPoint(self.maximum, 0)

        self.volumeProperty.SetColor(self.colorFunction)
        self.volumeProperty.SetScalarOpacity(self.opacityFunction)

        self._renderWindow.Render() 
        
    def valueChanged(self, value):
        self.updateTransferFunction()