from PyQt4.QtGui import QApplication#, QMainWindow, QFrame, QGridLayout, QWidget, QScrollBar, QLabel, QTabWidget, QPushButton, QHBoxLayout, QSpinBox, QFileDialog, QComboBox, QGroupBox, QVBoxLayout, QDial, QDialog, QSlider, QMenu, QLineEdit
from PyQt4.QtCore import Qt, QFile, QLatin1String, QSize
#from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import sys#, vtk, dicom, numpy as np, glob, xml.etree.ElementTree as ET, os, datetime, colorsys
#from ui.widgets.transferfunction import TransferFunction, TransferFunctionWidget
#from PySide.QtGui import QDialog as pysideQWidget
#from PySide.QtGui import QGridLayout as pysideQGridLayout
import GlobalVariables, TDViz, VTKTimerHeadTrack

'''
Created on Mar 10, 2015

@author: Bradley
'''
def main():
   
    GlobalVariables.init()
   
    app = QApplication([])

    File = QFile("darkorange.stylesheet")
    File.open(QFile.ReadOnly)
    StyleSheet = QLatin1String(File.readAll())    
 
    app.setStyleSheet(StyleSheet)

    tdviz = TDViz.TDVizCustom()
    tdviz.show()
    

    # TODO: Make sure you figure out this global import 3/10/2015
    if False:#GlobalVariables.isprojector:
        tdviz.setGeometry(1920, 0, 1280, 1024)
    else:
        tdviz.showFullScreen()    

    yscreenf = 1.0*tdviz._renWin.GetSize()[1]/1080.0

    cam = tdviz._ren.GetActiveCamera()
    cam.SetScreenBottomLeft(-262.5,148.5-148.5*2.0*yscreenf,-410)
    cam.SetScreenBottomRight(262.5,148.5-148.5*2.0*yscreenf,-410)
    cam.SetScreenTopRight(262.5,148.5,-410) 


    sys.exit(app.exec_())   
        
if __name__ == "__main__":
    main()
