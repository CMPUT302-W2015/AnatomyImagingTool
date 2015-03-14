import GlobalVariables

'''
Created on Mar 13, 2015

@see http://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another

@author: ANATOMY-IMAGING
'''
def mapValue(value, sensorMin, sensorMax, axis):
    
    if axis == "x":
        imageSpan = GlobalVariables.imageXDist # @UndefinedVariable
    elif axis == "y":
        imageSpan = GlobalVariables.imageYDist # @UndefinedVariable
    elif axis == "z":
        imageSpan = GlobalVariables.imageZDist # @UndefinedVariable
    
    # Figure out how 'wide' each range is
    sensorSpan = sensorMax - sensorMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - sensorMin) / float(sensorSpan)

    # Convert the 0-1 range into a value in the right range.
    return (valueScaled * imageSpan)