# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'appwindow.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AppWindow(object):
    def setupUi(self, AppWindow):
        AppWindow.setObjectName("AppWindow")
        AppWindow.resize(800, 600)
        AppWindow.setMinimumSize(QtCore.QSize(400, 600))
        self.centralwidget = QtWidgets.QWidget(AppWindow)
        self.centralwidget.setMinimumSize(QtCore.QSize(400, 600))
        self.centralwidget.setObjectName("centralwidget")
        AppWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(AppWindow)
        QtCore.QMetaObject.connectSlotsByName(AppWindow)

    def retranslateUi(self, AppWindow):
        _translate = QtCore.QCoreApplication.translate
        AppWindow.setWindowTitle(_translate("AppWindow", "MainWindow"))
