# -*- coding: utf-8 -*-
from PySide.QtCore import *
from PySide.QtGui import *
from widget import Separator, ColorPicker
from cst import ID_TO_NAME

class Picker(QHBoxLayout):
    def __init__(self):
        QBoxLayout.__init__(self)
        self.clrPicker = ColorPicker()
        self.lineStyle = QComboBox()
        self.lineStyle.addItems('-', '--', '-.', ':')
        
        


class DialogLineStyle(QDialog):
    applied = Signal(dict)
    def __init__(self, parent, data):
        QDialog.__init__(self, parent)
        self.setWindowTitle(u'Style des lignes')
        self.pickerList = {}
        layout = QVBoxLayout(self)
        flayout = QFormLayout()
        
        
        for graphId, name in ID_TO_NAME.items():
            d = data[graphId]
            lay = QHBoxLayout()
            clrPicker = ColorPicker()
            lineWidth = QDoubleSpinBox()
            lineWidth.setRange(0, 10)
            lineWidth.setSingleStep(0.5)
            lineStyle = QComboBox()
            lineStyle.addItems(('-', '--', '-.', ':'))
            
            clrPicker.setColor(d[0])
            lineWidth.setValue(d[1])
            lineStyle.setCurrentIndex(lineStyle.findText(d[2]))
            
            lay.addWidget(clrPicker)
            lay.addWidget(lineWidth)
            lay.addWidget(lineStyle)
            self.pickerList[graphId] = (clrPicker, lineWidth, lineStyle)
            flayout.addRow(name, lay)
        
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok | QDialogButtonBox.Apply,
                                      accepted=self.accept, rejected=self.reject)
        self.buttonBox.clicked.connect(self.slotButtonBox)
        layout.addLayout(flayout)
        layout.addWidget(Separator())
        layout.addWidget(self.buttonBox)
        
    def slotButtonBox(self, btn):
        if self.buttonBox.buttonRole(btn) == QDialogButtonBox.ApplyRole:
            self.applied.emit(self.getData())
        
    def getData(self):
        data = {}
        for graphId, wid in self.pickerList.items():
            clr, width, line = wid
            data[graphId] = (clr.color(), width.value(), line.currentText())
        return data