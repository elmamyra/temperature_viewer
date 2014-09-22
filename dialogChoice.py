
from PySide.QtCore import *  # @UnusedWildImport
from PySide.QtGui import *  # @UnusedWildImport
from cst import *  # @UnusedWildImport
from widget import Separator

class DialogChoice(QDialog):
    checked = Signal()
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setWindowTitle('Choix des graphiques')
        self.group = QButtonGroup(self)
        self.group.setExclusive(False)
        self._geometry = None
        
        layout = QVBoxLayout(self)
        
        for index, name in  ID_TO_NAME.items():
            cb = QCheckBox(name)
            self.group.addButton(cb, index)
            layout.addWidget(cb)
            
        buttonBox = QDialogButtonBox(QDialogButtonBox.Close, rejected=self.close)
        layout.addWidget(Separator())
        layout.addWidget(buttonBox)
        
        self.group.buttonClicked.connect(self.slotChecked)
    
    def slotChecked(self, cb):
        self.checked.emit()
    
    def getChecked(self):
        return [self.group.id(btn) for btn in self.group.buttons() if btn.isChecked()]
    
    def closeEvent(self, evt):
        self._geometry = self.geometry()
        
    def showEvent(self, evt):
        if self._geometry:
            self.setGeometry(self._geometry)
