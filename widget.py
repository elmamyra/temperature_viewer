from PySide.QtCore import *
from PySide.QtGui import *

class Separator(QFrame):
    def __init__(self, *args, **kwargs):
        QFrame.__init__(self, *args, **kwargs)
        self.setLineWidth(1)
        self.setMidLineWidth(0)
        self.setOrientation(Qt.Horizontal)
        
    def setOrientation(self, orientation):
        if orientation == Qt.Vertical:
            self.setFrameShape(QFrame.VLine)
            self.setFrameShadow(QFrame.Sunken)
            self.setMinimumSize(2, 0)
        else:
            self.setFrameShape(QFrame.HLine)
            self.setFrameShadow(QFrame.Sunken)
            self.setMinimumSize(0, 2)
        self.updateGeometry()
        
    def orientation(self):
        return Qt.Vertical if self.frameStyle() & QFrame.VLine == QFrame.VLine else Qt.Horizontal
    
    

class ColorPicker(QPushButton):
    colorChanged = Signal(str)
    def __init__(self, color=""):
        QPushButton.__init__(self)
        self.setObjectName("pickerButton")
        self.setColor(color)
        self.setMaximumWidth(32)
        self.pressed.connect(self.onColorPicker)
        
    def setColor(self, color):
        self._color = color
        self.colorChanged.emit(color)
        if self._color:
            self.setStyleSheet("""QPushButton#pickerButton {{ background-color: {}; 
            border: 2px solid #8f8f91;
             border-radius: 6px;}}""".format(self._color))
        else:
            self.setStyleSheet("""QPushButton#pickerButton { border: 2px solid #8f8f91;
             border-radius: 6px;}""")
            
    def color(self):
        return self._color
    
    def onColorPicker(self):
        qcolor = QColor()
        qcolor.setNamedColor(self._color)
        dlg = QColorDialog(qcolor, self)
        
        if dlg.exec_():
            self.setColor(dlg.currentColor().name())
            self.clearFocus()