# -*- coding: utf-8 -*-
from PySide.QtCore import *  # @UnusedWildImport
from PySide.QtGui import *  # @UnusedWildImport
from dialogConnect import DialogConnect
from dialogChoice import DialogChoice
from dialogLimit import DialogLimit
from dialogLineStyle import DialogLineStyle
import os
os.environ["QT_API"] = "pyside"
import matplotlib
matplotlib.use('Qt4Agg')
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt4 import NavigationToolbar2QT
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.dates import MO
from mpl_toolkits.axes_grid.parasite_axes import SubplotHost
import resource_rc  # @UnusedImport
from cst import *  # @UnusedWildImport
matplotlib.rcParams['backend.qt4']='PySide'
import MySQLdb
import sys


class TemperatureViewer(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setupUi()
        self.conn = self.cur = None
        self.connData = None
        self.currentData = []
        self.limitData = {}
        self.lineStyleData = {}
        self.lineList = []
        self.ax = None
        self.show()
        self.dialogChoice = DialogChoice(self, self.choiceAction)
        self.dialogChoice.checked.connect(self.slotGraphChecked)
        self.dialogLimit = self.dialogLineStyle = None
        self.readSettings()
        self._isConnected = self.connectDb()
    
#     def test(self):
#         print 'reject'
    
    def readSettings(self):
        s = QSettings()
        choiceState = True if s.value('dialogChoiceState', 'true') == 'true' else False
        if choiceState:
            self.choiceAction.setChecked(True)
            self.dialogChoice.show()
        self.dialogChoice.setGeometry(s.value('dialogChoiceGeometry', self.dialogChoice.geometry()))
        
        defaultColors = {}
        for i, graphId in enumerate(ID_TO_NAME.keys()):
            defaultColors[graphId] = (COLORS[i], 1, '-')
        
        self.lineStyleData = s.value('lineStyle', defaultColors)
        
        self.restoreGeometry(s.value('geometry', self.saveGeometry()))
        
#         s.beginGroup('limit')
        defaultLimit = {TEMP: None, MILLIS: None, PCHAUF: None, HC:None, MOI:None}
        self.limitData = s.value('limit', defaultLimit)
#         for graphId, text in ((TEMP, 'temp'), (MILLIS, 'millis'), (PCHAUF, 'pchauf'), (HC, 'hc'), (MOI, 'moi')):
#             self.limitData[graphId] = (int(s.value(text+'Min')), int(s.value(text+'Max'))) if s.value(text+'Min') else None
        
        s.endGroup()
        s.beginGroup('connexion')
        self.connData = {
            'host': s.value('host', 'localhost'),
            'user': s.value('user', 'root'),
            'passwd': s.value('passwd', ''),
            'db': s.value('db', 'chaudiere'),
            'table': s.value('table', 'releves')}
        if not s.allKeys():
            self.connectAction.trigger()
        
      
    def connectDb(self):
        if not self.connData:
            QMessageBox.critical(self, "Erreur", u"Aucun paramètre de connection")
            return
        
        try:
            self.conn = MySQLdb.connect(self.connData['host'], self.connData['user'], self.connData['passwd'], 
                                        self.connData['db'], unix_socket="/opt/lampp/var/mysql/mysql.sock")
            self.cur = self.conn.cursor()
            
            qdateMin = QDate.fromString(str(self.getFirstDate()), "yyyy-MM-dd")
            self.dateEdit.setDate(QSettings().value('date') or qdateMin)
            print qdateMin
            self.dateEdit.setMinimumDate(qdateMin)
            return True
        except MySQLdb.Error, e:
            err = "Error {}: {}".format(e.args[0], e.args[1])
            QMessageBox.critical(self, "Erreur", u"Erreur lors de connection à la base de donnée: \n{}".format(err))
            return False
    
    def currentPeriod(self):
        return self.comboPeriod.currentIndex()
    
    def setPeriod(self, period):
        index = self.comboPeriod.findData(period)
        print period, index
        self.comboPeriod.setCurrentIndex(index)
    
    def getFirstDate(self):
#         if self._isConnected:
        self.cur.execute("SELECT date FROM {} ORDER BY date LIMIT 1".format(self.connData['table']))
        return self.cur.fetchone()[0]
    
    def computeData(self):
        if not self.testConnection():
            return
        
        period = self.comboPeriod.currentIndex()
        if period == DAY:
            start = self.dateEdit.dateTime()
        else:
            start = self.dateEdit.date()
            
        if period == WEEK:
            end = start.addDays(7)
        else:
            end = {DAY: start.addDays, MONTH: start.addMonths, YEAR:  start.addYears}[period](1)
        
        self.cur.execute("""
                    SELECT DATE_ADD(date, INTERVAL TIME_TO_SEC(heure) SECOND) as date_time, {columns}
                    FROM {table}
                    WHERE DATE_ADD(date, INTERVAL TIME_TO_SEC(heure) SECOND) 
                    BETWEEN '{startDate}' AND '{endDate}'
                    ORDER BY date_time""".format(columns = ', '.join(TABLE_NAME),
                                                 table = self.connData['table'], 
                                                 startDate = start.toPython(), 
                                                 endDate = end.toPython()))
        
        self.currentData = zip(*self.cur.fetchall())
        if self.currentData:
            self.datetimeData = self.currentData[DATE_TIME]
        
    def createAxes(self):
        self.fig.clear()
        self.lineList = []
        self.ax = SubplotHost(self.fig, 111)
        self.ax.toggle_axisline(False)
        self.ax.plot(self.datetimeData, [None]*len(self.datetimeData))
        self.fig.add_subplot(self.ax)
        self.fig.set_tight_layout(True)
        if self.limitData[TEMP]:
            self.ax.set_ylim(*self.limitData[TEMP])
        
        
    def createLocator(self):
        if self.currentPeriod() == DAY:
            self.ax.xaxis.set_major_locator(mdates.HourLocator())
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Hh'))
            self.ax.xaxis.set_minor_locator(mdates.MinuteLocator((15, 30, 45)))
        elif self.currentPeriod() == WEEK:
            self.ax.xaxis.set_major_locator(mdates.DayLocator())
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%a %d %b'))
            self.ax.xaxis.set_minor_locator(mdates.HourLocator((6, 12, 18)))
        elif self.currentPeriod() == MONTH:
            self.ax.xaxis.set_major_locator(mdates.WeekdayLocator(MO))
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))  
            self.ax.xaxis.set_minor_locator(mdates.DayLocator())
        elif self.currentPeriod() == YEAR:
            self.ax.xaxis.set_major_locator(mdates.MonthLocator())
            self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))  
            self.ax.xaxis.set_minor_locator(mdates.WeekdayLocator(MO))
        
        self.ax.grid(b=True, which='major', color=(0.4,0.4,0.4), linestyle='--')
        self.ax.grid(b=True, which='minor', color=(0.6,0.6,0.6), linestyle=':')
        self.ax.set_autoscalex_on(False) 

    def plot(self):
        checkedGraph = self.dialogChoice.getChecked()
        if not checkedGraph:
            return
        specialGraph = (MILLIS, PCHAUF, HC, MOI)
        
        offset = 0
        patchs = []
        labels = []
        
        for graphId in checkedGraph:
            clr, width, style = self.lineStyleData[graphId]
#             clr = self.idToColors[graphId]
            if graphId in specialGraph:
                
                ax = self.ax.twinx()
                new_fixed_axis = ax.get_grid_helper().new_fixed_axis
                ax.axis["right"] = new_fixed_axis(loc="right",
                                        axes=ax,
                                        offset=(offset, 0))
                offset += 60
                ax.set_ylabel(ID_TO_NAME[graphId])
                ax.yaxis.label.set_color(clr)
                if self.limitData[graphId]:
                    ax.set_ylim(*self.limitData[graphId])
            else:
                ax = self.ax
            
            meth = ax.step if graphId == HC else ax.plot
            l = meth(self.datetimeData, self.currentData[graphId], color=clr, linewidth=width, linestyle=style)
            self.lineList.append(l[0])
            patchs.append(mpatches.Patch(color=clr))
            labels.append(ID_TO_NAME[graphId])

        self.fig.legend(patchs, labels, 'upper center', prop={'size':10})
    
    def run(self, computeData=True):
        if not self.testConnection():
            return

        if computeData:
            self.computeData()
        if self.currentData:
            self.createAxes()
            self.plot()
            self.createLocator()
            self.canvas.draw()
    
    def testConnection(self):
        if self.conn and self.conn.open:
            return True
        else:
            QMessageBox.warning(self, "Pas de connection", u"La base de donnée n'est pas connecté")
            return False
    
    def slotChoice(self):
        if self.choiceAction.isChecked():
            self.dialogChoice.show()
        else:
            self.dialogChoice.close()
            
    def slotToggleChoiceCheck(self):
        self.choiceAction.toggle()
        self.slotChoice()
            
    def slotPeriodChanged(self, index):
        self.run()
    
    def slotGraphChecked(self):
        self.run(not bool(self.currentData))
    
    def slotConnect(self):
        dlg = DialogConnect(self, self.connData)
        if dlg.exec_():
            self.connData = dlg.getData()
            s = QSettings()
            s.beginGroup('connexion')
            s.setValue('host', self.connData['host'])
            s.setValue('user', self.connData['user'])
            s.setValue('passwd', self.connData['passwd'])
            s.setValue('db', self.connData['db'])
            s.setValue('table', self.connData['table'])
            if self.conn and self.conn.open:
                self.conn.close()
            self.connectDb()
    
    def slotPreviousDate(self):
        self.movePeriod(-1)
    
    def slotNextDate(self):
        self.movePeriod(1)
        
    def movePeriod(self, direction):
        dt = self.dateEdit.date()
        period = self.comboPeriod.itemData(self.comboPeriod.currentIndex())
        if period == WEEK:
            dt = dt.addDays(7*direction)
        else:
            dt = {DAY: dt.addDays, MONTH: dt.addMonths, YEAR: dt.addYears}[period](1*direction)
        
        self.dateEdit.setDate(dt)
        self.run()
        
    def closeEvent(self, event):
        s = QSettings()
        s.setValue('geometry', self.saveGeometry())
        s.setValue('dialogChoiceState', self.choiceAction.isChecked())
        s.setValue('dialogChoiceGeometry', self.dialogChoice.geometry())
        s.setValue('date', self.dateEdit.date())
        s.setValue('limit', self.limitData)
        s.setValue('lineStyle', self.lineStyleData)
        s.beginGroup('limit')
        
#         for graphId, text in ((TEMP, 'temp'), (MILLIS, 'millis'), (PCHAUF, 'pchauf'), (HC, 'hc'), (MOI, 'moi')):
#             d = self.limitData[graphId]
#             if d:
#                 s.setValue(text+'Min', d[0])
#                 s.setValue(text+'Max', d[1])
#             else:
#                 s.setValue(text+'Min', None)
#                 s.setValue(text+'Max', None)
                
    def slotCanvasPressed(self, e):
        self.canvas.setFocus()
        if e.xdata and int(e.xdata) and e.button == 3:
            dt = QDateTime.fromTime_t(mdates.num2epoch(e.xdata)).date()
            monday = QDate(dt)
            while monday.dayOfWeek() != 1:
                monday = monday.addDays(-1)
            
            menu = QMenu(self)
            dayAction = QAction(u"jour: {}".format(dt.toString("dddd d MMMM")), self)
            weekAction = QAction(u"semaine du: {}".format(monday.toString("dddd d MMMM")), self)
            monthAction = QAction(u"mois de: {}".format(dt.toString("MMMM")), self)
            
            period = self.currentPeriod()
            
            if period == WEEK:
                menu.addAction(dayAction)
            elif period == MONTH:
                menu.addAction(dayAction)
                menu.addAction(weekAction)
            elif period == YEAR:
                menu.addAction(dayAction)
                menu.addAction(weekAction)
                menu.addAction(monthAction)
            else:
                return
                
            canvasPos = self.canvas.mapTo(self, self.canvas.geometry().topLeft())
            y = self.canvas.geometry().height() - e.y + canvasPos.y() - self.canvas.pos().x()
            x = e.x + self.canvas.pos().y()
            pos = QPoint(x, y)
            act = menu.exec_(self.mapToGlobal(pos))
            
            if act == dayAction:
                self.dateEdit.setDate(dt)
                period = DAY
            elif act == weekAction:
                self.dateEdit.setDate(monday)
                period = WEEK
            elif act == monthAction:
                self.dateEdit.setDate(QDate(dt.year(), dt.month(), 1))
                period = MONTH
            self.setPeriod(period)  
            self.run()
    
    
    
    def slotCalendar(self):
        self.canvas.setFocus()
        self.run()
    
    
    def slotLimit(self):
        if self.dialogLimit:
            self.dialogLimit.reject()
            self.dialogLimit = None
        else:
            self.dialogLimit = dlg = DialogLimit(self, self.limitData)
            dlg.accepted.connect(self.slotLimitAccepted)
            dlg.rejected.connect(self.slotLimitRejected)
            dlg.applied.connect(self.slotLimitApplied)
            dlg.show()
            
    def slotLimitAccepted(self):
        self.limitAction.setChecked(False)
        self.limitData = self.dialogLimit.getData()
        self.dialogLimit = None
        self.run(False)
    
    def slotLimitRejected(self):
        self.limitAction.setChecked(False)
        self.dialogLimit = None
    
    def slotLimitApplied(self, limitData):
        self.limitData = limitData
        self.run(False)
        
                    
    def slotLineStyle(self):
        if self.dialogLineStyle:
            self.dialogLineStyle.reject()
            self.dialogLineStyle = None
        else:
            self.dialogLineStyle = dlg = DialogLineStyle(self, self.lineStyleData)
            dlg.accepted.connect(self.slotLineStyleAccepted)
            dlg.rejected.connect(self.slotLineStyleRejected)
            dlg.applied.connect(self.slotLineStyleApplied)
            dlg.show()
    
    def slotLineStyleAccepted(self):
        self.lineStyleAction.setChecked(False)
        self.lineStyleData = self.dialogLineStyle.getData()
        self.dialogLineStyle = None
        self.run(False)
    
    def slotLineStyleRejected(self):
        self.lineStyleAction.setChecked(False)
        self.dialogLineStyle = None
    
    def slotLineStyleApplied(self, lineStyleData):
        self.lineStyleData = lineStyleData
        self.run(False)
    
    def setupUi(self):
        def addGlobalAction(seq, slot):
            act = QAction(self)
            act.triggered.connect(slot)
            act.setShortcut(QKeySequence(seq))
            act.setShortcutContext(Qt.ApplicationShortcut)
            self.addAction(act)
            
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        layout = QVBoxLayout(centralWidget)
        
        self.setWindowTitle(u"Visionneuse de température")
        self.setWindowIcon(QIcon(":/icon/graph"))
        toolbar = QToolBar(self)
        quitAction = QAction(QIcon(":/icon/quit"), u'Quitter', self, triggered=self.close)
        runAction = QAction(QIcon(":/icon/exec"), u'Afficher la courbe', self, triggered=self.run)
        self.connectAction = QAction(QIcon(":/icon/connect"), u'Paramètre de connection', self, triggered=self.slotConnect)
        previousAction = QAction(QIcon(":/icon/previous"), u"Date précédante", self, triggered=self.slotPreviousDate)
        nextAction = QAction(QIcon(":/icon/next"), u"Date suivante", self, triggered=self.slotNextDate)
        self.choiceAction = QAction(QIcon(":/icon/check"), u"Choix des graphiques", self, triggered=self.slotChoice, checkable=True)
        self.limitAction = QAction(QIcon(":/icon/slider"), u"Échelles", self, triggered=self.slotLimit)
        self.lineStyleAction = QAction(QIcon(":/icon/line"), u"Style de lignes", self, triggered=self.slotLineStyle)
        self.lineStyleAction.setCheckable(True)
        addGlobalAction(Qt.CTRL + Qt.Key_Space, self.slotToggleChoiceCheck)
        addGlobalAction(Qt.Key_Left, self.slotPreviousDate)
        addGlobalAction(Qt.Key_Right, self.slotNextDate)
        self.comboPeriod = QComboBox()
        for text, data in (('jour', DAY), ('semaine', WEEK), ('mois', MONTH), (u'année', YEAR)):
            self.comboPeriod.addItem(text, data)
        self.comboPeriod.currentIndexChanged.connect(self.slotPeriodChanged)
        
        format_ = "ddd dd MMM yyyy HH'h'"
        self.dateEdit = QDateTimeEdit()
        self.dateEdit.setDisplayFormat(format_)
        self.dateEdit.setCalendarPopup(True)
        self.dateEdit.setMinimumWidth(180)
        self.dateEdit.calendarWidget().clicked .connect(self.slotCalendar)
        
        toolbar.addAction(quitAction)
        toolbar.addAction(self.connectAction)
        toolbar.addSeparator()
        toolbar.addWidget(self.dateEdit)
        toolbar.addAction(runAction)
        toolbar.addSeparator()
        toolbar.addAction(self.choiceAction)
        toolbar.addWidget(self.comboPeriod)
        toolbar.addAction(previousAction)
        toolbar.addAction(nextAction)
        toolbar.addSeparator()
        toolbar.addAction(self.limitAction)
        toolbar.addAction(self.lineStyleAction)
        self.addToolBar(toolbar)
        
        self.fig = Figure(facecolor=(1,1,1), edgecolor=(0,0,0))
        self.canvas = FigureCanvas(self.fig)
        self.canvas.mpl_connect('button_press_event', self.slotCanvasPressed)
        layout.addWidget(self.canvas)
        centralWidget.setLayout(layout)
        

app = QApplication(sys.argv)
translatorQt=QTranslator ()
locale = QLocale.system().name()
translatorQt.load("qt_" + locale,   
                QLibraryInfo.location(QLibraryInfo.TranslationsPath))

app.installTranslator(translatorQt)
  
QCoreApplication.setOrganizationName("temperature_viewer")
main = TemperatureViewer()
sys.exit(app.exec_())