# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from __future__ import print_function
from PyQt5 import QtCore, QtGui, QtWidgets
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import time
import threading

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'

class Ui_MainWindow(object):
    def setup(self):
        # Read Configuration File
        conf = open('configuration.inf', 'r')
        lines = conf.readlines()

        i = 0
        self.headers = []
        self.TAs = []
        self.free = []
        self.occupancy = []

        for line in lines:
            if (line.strip() and not (line.strip()[0] == '#')):
                data = line.split(': ')[-1]
                if i == 0:
                    self.SPREADSHEET_ID = data.strip('\n')
                elif i == 1:
                    self.RANGE_NAME_1 = data.strip('\n')
                elif i == 2:
                    self.RANGE_NAME_1 = self.RANGE_NAME_1 + "!" + data.strip('\n')
                elif i == 3:
                    self.RANGE_NAME_2 = data.strip('\n') + "!B"
                elif i == 4:
                    self.count = int(data.strip('\n'))
                elif i < 4 + self.count + 1:
                    self.TAs.append([])
                    self.occupancy.append([])
                    self.free.append(1)

                    self.headers.append(data.strip('\n'))
                #print(line, end = '')
                i = i + 1
        print (self.headers)
        self.allow_run = False
        self.curr_row_1 = 2
        self.curr_row_2 = 2
        
    def begin(self):
        if not self.allow_run:
            self.allow_run = True
            _translate = QtCore.QCoreApplication.translate
            self.t = threading.Thread(target=self.allocate)
            self.t.start()
            self.commandLinkButton.setText(_translate("MainWindow", "Stop"))
            print('Thread Started')

        else:
            self.allow_run = False
            _translate = QtCore.QCoreApplication.translate
            self.t.join()
            self.commandLinkButton.setText(_translate("MainWindow", "Start"))
            print('Thread Stopped')

    def allocate(self):
        _translate = QtCore.QCoreApplication.translate

        # Connect to Google API
        store = file.Storage('token.json')
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
            creds = tools.run_flow(flow, store)
        service = build('sheets', 'v4', http=creds.authorize(Http()))

        while self.allow_run:
            result = service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID,
                                                        range = (self.RANGE_NAME_1 + str(self.curr_row_1) + ':' + chr(ord(self.RANGE_NAME_1[-1]) + 2))).execute()
            values = result.get('values', [])
            result = service.spreadsheets().values().get(spreadsheetId=self.SPREADSHEET_ID,
                                                        range = (self.RANGE_NAME_2 + str(self.curr_row_2) + ':B')).execute()
            done = result.get('values', [])
            self.curr_row_1 = self.curr_row_1 + len(values)
            self.curr_row_2 = self.curr_row_2 + len(done)
            
            if done:
                for row in done:
                    if row:
                        self.free[int(row[0][0]) - 1] = 1
                        self.occupancy[int(row[0][0]) - 1] = []

            if not values:
                print('No data found.')
            else:
                #print('Name, Major:')
                for row in values:
                    if row:
                        # Print columns A and E, which correspond to indices 0 and 4.
                        print('%s, %s, %s' % (row[0], row[1], row[2]))
                        items = row[2].split(', ')
                        for item in items:
                           self.TAs[int(item[0]) - 1].append([row[0].upper(), row[1]])
            
            for i in range(0, self.count):
                if ((self.free[i] == 1) and (self.TAs[i])):
                    j = 0
                    while (len(self.TAs[i]) > j) and (self.TAs[i][j][0] in [sublist[0] if sublist else [] for sublist in self.occupancy]):
                        j = j + 1
                    if (j == len(self.TAs[i])):
                        continue
                    if not (self.TAs[i][j][0] in [sublist[0] if sublist else [] for sublist in self.occupancy]):
                        self.occupancy[i] = self.TAs[i][j]
                        self.TAs[i].pop(j)
                        self.free[i] = 0

            print(self.TAs)
            print(self.free)
            print([sublist[0] if sublist else [] for sublist in self.occupancy])

            for i in range(0, self.count * 3):
                if (i % 3 == 1):
                    self.labels[i].setText(_translate("MainWindow", str(self.occupancy[i // 3][0] if self.occupancy[i // 3] else '')))
                if (i % 3 == 2):
                    self.labels[i].setText(_translate("MainWindow", str(self.occupancy[i // 3][1] if self.occupancy[i // 3] else '')))

            for i in range(0, self.count):
                self.lcds[i].setProperty("intValue", len(self.TAs[i]))
            
            time.sleep(4)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1914, 1065)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralWidget.sizePolicy().hasHeightForWidth())
        self.centralWidget.setSizePolicy(sizePolicy)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout.setContentsMargins(11, 11, 11, 11)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setObjectName("verticalLayout")
        
        self.commandLinkButton = QtWidgets.QCommandLinkButton(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.commandLinkButton.sizePolicy().hasHeightForWidth())
        self.commandLinkButton.setSizePolicy(sizePolicy)
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.commandLinkButton.clicked.connect(self.begin);

        self.verticalLayout.addWidget(self.commandLinkButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")

        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        
        self.verticalLayout.addLayout(self.gridLayout_2)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1914, 26))
        self.menuBar.setObjectName("menuBar")
        self.menuEE_618_Crib_Session_Token_System = QtWidgets.QMenu(self.menuBar)
        self.menuEE_618_Crib_Session_Token_System.setObjectName("menuEE_618_Crib_Session_Token_System")
        MainWindow.setMenuBar(self.menuBar)
        
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.menuBar.addAction(self.menuEE_618_Crib_Session_Token_System.menuAction())
        
        self.labels = []
        self.lcds = []
        
        font1 = QtGui.QFont()
        font1.setPointSize(15)
        font1.setBold(True)
        font1.setUnderline(True)
        font1.setWeight(75)

        font2 = QtGui.QFont()
        font2.setPointSize(15)
        
        for i in range(0, min(18, self.count * 3)):
            self.labels.append(QtWidgets.QLabel(self.centralWidget))
            self.labels[i].setFont(font1 if (i % 3 == 0) else font2)
            self.labels[i].setAlignment(QtCore.Qt.AlignCenter)
            self.labels[i].setObjectName("label_" + str(i))
            self.gridLayout.addWidget(self.labels[i], i % 3, i // 3, 1, 1)

        for i in range(0, min(6, self.count)):
            self.lcds.append(QtWidgets.QLCDNumber(self.centralWidget))
            self.lcds[i].setObjectName("lcdNumber_" + str(i))
            self.gridLayout.addWidget(self.lcds[i], 3, i, 1, 1)

        for i in range(0, max(0, (self.count - 6) * 3)):
            self.labels.append(QtWidgets.QLabel(self.centralWidget))
            self.labels[i + 18].setFont(font1 if (i % 3 == 0) else font2)
            self.labels[i + 18].setAlignment(QtCore.Qt.AlignCenter)
            self.labels[i + 18].setObjectName("label_" + str(i + 18))
            self.gridLayout_2.addWidget(self.labels[i + 18], i % 3, i // 3, 1, 1)

        for i in range(0, max(0, (self.count - 6))):
            self.lcds.append(QtWidgets.QLCDNumber(self.centralWidget))
            self.lcds[i + 6].setObjectName("lcdNumber_" + str(i + 6))
            self.gridLayout_2.addWidget(self.lcds[i + 6], 3, i, 1, 1)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Token System"))
        self.commandLinkButton.setText(_translate("MainWindow", "Start"))

        for i in range(0, self.count * 3):
            if (i % 3 == 0):
                self.labels[i].setText(_translate("MainWindow", self.headers[i // 3]))

        self.menuEE_618_Crib_Session_Token_System.setTitle(_translate("MainWindow", "EE 618 Crib Session Token System"))


if __name__ == "__main__":
    import sys
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setup()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

