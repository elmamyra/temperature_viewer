# -*- coding: utf-8 -*-
from PySide.QtCore import *
from PySide.QtGui import *
from widget import Separator
from cst import MILLIS, PCHAUF, HC, MOI, TEMP, ID_TO_NAME
import sys

class Picker(QGroupBox):
    def __init__(self, graphId, data, min_, max_, title='', mult=1):
        QGroupBox.__init__(self)
        self.mult = mult
        self.setCheckable(True)
        layout = QHBoxLayout(self)
        if title:
            self.setTitle(title)
        else:
            self.setTitle(ID_TO_NAME[graphId])
        
        self.minSpin = QSpinBox()
        self.maxSpin = QSpinBox()
        self.minSpin.setRange(-1000, 1000)
        self.maxSpin.setRange(-1000, 1000)
        
        if data:
            print data
            self.minSpin.setValue(data[0]/mult)
            self.maxSpin.setValue(data[1]/mult)
        else:
            self.minSpin.setValue(min_)
            self.maxSpin.setValue(max_)
            self.setChecked(False)

        layout.addWidget(QLabel('min:'))
        layout.addWidget(self.minSpin)
        layout.addWidget(QLabel('max:'))
        layout.addWidget(self.maxSpin)
        layout.addStretch(1)
        
    def getData(self):
        if self.isChecked():
            return (self.minSpin.value()*self.mult, self.maxSpin.value()*self.mult)
        else:
            return None
        
        
class DialogLimit(QDialog):
    applied = Signal(dict)
    def __init__(self, parent, data):
        QDialog.__init__(self, parent)
        self.setWindowTitle(u'Échelles')
        
        layout = QVBoxLayout(self)
        self.tempPicker = Picker(TEMP, data[TEMP], -10, 30, u"température")
        self.millisPicker = Picker(MILLIS, data[MILLIS], 0, 200, u"compteur de millisecondes (×10e7)", 10**7)
        self.pchaufPicker = Picker(PCHAUF, data[PCHAUF], 0, 256)
        self.hcPicker = Picker(HC, data[HC], 0, 10)
        self.moiPicker = Picker(MOI, data[MOI], 30, 90)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok | QDialogButtonBox.Apply,
                                      accepted=self.accept, rejected=self.reject)
        
        self.buttonBox.clicked.connect(self.slotButtonBox)
        
        layout.addWidget(self.tempPicker)
        layout.addWidget(self.millisPicker)
        layout.addWidget(self.pchaufPicker)
        layout.addWidget(self.hcPicker)
        layout.addWidget(self.moiPicker)
        layout.addWidget(Separator())
        layout.addWidget(self.buttonBox)
    
    def slotButtonBox(self, btn):
        if self.buttonBox.buttonRole(btn) == QDialogButtonBox.ApplyRole:
            self.applied.emit(self.getData())
    
    def getData(self):
        return {TEMP: self.tempPicker.getData(),
                MILLIS: self.millisPicker.getData(),
                PCHAUF: self.pchaufPicker.getData(),
                HC: self.hcPicker.getData(),
                MOI: self.moiPicker.getData()}
        
