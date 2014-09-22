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