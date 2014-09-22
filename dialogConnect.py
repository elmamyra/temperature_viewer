# -*- coding: utf-8 -*-
from PySide.QtCore import *
from PySide.QtGui import *
from widget import Separator


class DialogConnect(QDialog):
    def __init__(self, parent, connData):
        QDialog.__init__(self, parent)
        self.setWindowTitle(u'Paramètre de connection')
        
        layout = QVBoxLayout(self)
        flayout = QFormLayout()
        flayout.setLabelAlignment(Qt.AlignRight)
        self.hostLine = QLineEdit(connData['host'])
        self.userLine = QLineEdit(connData['user'])
        self.passwdLine = QLineEdit(connData['passwd'])
        self.dbLine = QLineEdit(connData['db'])
        self.tableLine = QLineEdit(connData['table'])
        
        self.passwdLine.setEchoMode(QLineEdit.Password)
        
        flayout.addRow(u'Hôte:', self.hostLine)
        flayout.addRow(u'Utilisateur:', self.userLine)
        flayout.addRow(u'Mot de passe:', self.passwdLine)
        flayout.addRow(u'Base de donnée:', self.dbLine)
        flayout.addRow(u'Nom de la table:', self.tableLine)
        
        buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel, accepted=self.accept, rejected=self.reject)
        buttonBox.addButton(QPushButton(u'Connecter'), QDialogButtonBox.AcceptRole)
        
        layout.addLayout(flayout)
        layout.addWidget(Separator())
        layout.addWidget(buttonBox)
    
    def getData(self):
        return {'host': self.hostLine.text(),
         'user': self.userLine.text(),
         'passwd': self.passwdLine.text(),
         'db': self.dbLine.text(),
         'table': self.tableLine.text()
         
         }
        
        
