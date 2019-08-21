# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Admin\Google Drive\1. Software Engineering\Python\DESIGN CONVERT\SamplifyGUISketch.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDir, Qt
import os
import settings

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 571)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(60, 10, 160, 83))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.librariesTreeView = QtWidgets.QTreeView(self.gridLayoutWidget)
        self.librariesTreeView.setObjectName("librariesTreeView")
        self.gridLayout.addWidget(self.librariesTreeView, 0, 0, 1, 1)
        self.gridLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget_2.setGeometry(QtCore.QRect(470, 10, 160, 83))
        self.gridLayoutWidget_2.setObjectName("gridLayoutWidget_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gridLayoutWidget_2)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.librariesContentsColumnView = QtWidgets.QColumnView(self.gridLayoutWidget_2)
        self.librariesContentsColumnView.setObjectName("librariesContentsColumnView")
        self.gridLayout_2.addWidget(self.librariesContentsColumnView, 0, 0, 1, 1)
        self.addLibraryPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.addLibraryPushButton.setGeometry(QtCore.QRect(50, 100, 84, 25))
        self.addLibraryPushButton.setObjectName("addLibraryPushButton")
        self.removeLibraryPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.removeLibraryPushButton.setGeometry(QtCore.QRect(150, 100, 84, 25))
        self.removeLibraryPushButton.setObjectName("removeLibraryPushButton")
        self.gridLayoutWidget_3 = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget_3.setGeometry(QtCore.QRect(50, 150, 160, 83))
        self.gridLayoutWidget_3.setObjectName("gridLayoutWidget_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.gridLayoutWidget_3)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")

        self.outputTreeView = QtWidgets.QTreeView(self.gridLayoutWidget_3)
        self.outputTreeView.setObjectName("outputTreeView")

        self.gridLayout_3.addWidget(self.outputTreeView, 0, 0, 1, 1)
        self.gridLayoutWidget_4 = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget_4.setGeometry(QtCore.QRect(470, 150, 160, 81))
        self.gridLayoutWidget_4.setObjectName("gridLayoutWidget_4")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.gridLayoutWidget_4)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.outputPropertiesColumnView = QtWidgets.QColumnView(self.gridLayoutWidget_4)
        self.outputPropertiesColumnView.setObjectName("outputPropertiesColumnView")
        self.gridLayout_4.addWidget(self.outputPropertiesColumnView, 0, 0, 1, 1)
        self.openFileSystemManagerPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.openFileSystemManagerPushButton.setGeometry(QtCore.QRect(50, 240, 84, 25))
        self.openFileSystemManagerPushButton.setObjectName("openFileSystemManagerPushButton")
        self.openFileSystemManagerPushButton.clicked.connect(self.buttonClickedFileSystemManager)


        self.gridLayoutWidget_5 = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget_5.setGeometry(QtCore.QRect(50, 280, 591, 181))
        self.gridLayoutWidget_5.setObjectName("gridLayoutWidget_5")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.gridLayoutWidget_5)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.consoleVerticalSlider = QtWidgets.QSlider(self.gridLayoutWidget_5)
        self.consoleVerticalSlider.setOrientation(QtCore.Qt.Vertical)
        self.consoleVerticalSlider.setObjectName("consoleVerticalSlider")
        self.gridLayout_5.addWidget(self.consoleVerticalSlider, 0, 1, 1, 1)
        self.consoleListView = QtWidgets.QListView(self.gridLayoutWidget_5)
        self.consoleListView.setObjectName("consoleListView")
        self.gridLayout_5.addWidget(self.consoleListView, 0, 0, 1, 1)
        self.samplifyStartPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.samplifyStartPushButton.setGeometry(QtCore.QRect(63, 480, 131, 25))
        self.samplifyStartPushButton.setObjectName("samplifyStartPushButton")
        self.samplifyApplySettingsPushButton = QtWidgets.QPushButton(self.centralwidget)
        self.samplifyApplySettingsPushButton.setGeometry(QtCore.QRect(450, 480, 121, 25))
        self.samplifyApplySettingsPushButton.setObjectName("samplifyApplySettingsPushButton")
        self.syncEnableCheckbox = QtWidgets.QCheckBox(self.centralwidget)
        self.syncEnableCheckbox.setGeometry(QtCore.QRect(250, 480, 111, 21))
        self.syncEnableCheckbox.setObjectName("syncEnableCheckbox")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.addLibraryPushButton.setText(_translate("MainWindow", "Add"))
        self.removeLibraryPushButton.setText(_translate("MainWindow", "Remove"))
        self.openFileSystemManagerPushButton.setText(_translate("MainWindow", "Modify"))
        self.samplifyStartPushButton.setText(_translate("MainWindow", "Samplify!"))
        self.samplifyApplySettingsPushButton.setText(_translate("MainWindow", "Apply Settings"))
        self.syncEnableCheckbox.setText(_translate("MainWindow", "SYNC ON/OFF"))

    def drawOutputTreeView(self, root, tree):

        model = QtWidgets.QFileSystemModel()
        model.setRootPath('')
        tree.setModel(model)
        tree.setRootIndex(model.index(root))

    def buttonClickedFileSystemManager(self):
        super(Ui_ModifyOutputWindow).__init__()
        self.modifyOutputWindow = Ui_ModifyOutputWindow()
        self.modifyOutputWindow.show()




class Ui_ModifyOutputWindow(QtWidgets.QMainWindow):

    def setupUi(self, ModifyOutputWindow):
        super(Ui_MainWindow).__init__()
        ModifyOutputWindow.setObjectName("File System Manager")

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ModifyOutputWindow = QtWidgets.QMainWindow()

    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.drawOutputTreeView(settings.output_path, ui.outputTreeView)


    MainWindow.show()
    sys.exit(app.exec_())

