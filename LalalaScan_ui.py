# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LalalaScan_ui.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(873, 593)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.listWidgetPlugin = QtWidgets.QListWidget(self.centralwidget)
        self.listWidgetPlugin.setGeometry(QtCore.QRect(642, 30, 221, 541))
        self.listWidgetPlugin.setObjectName("listWidgetPlugin")
        self.pushButtonStart = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonStart.setEnabled(True)
        self.pushButtonStart.setGeometry(QtCore.QRect(484, 7, 71, 31))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.pushButtonStart.setFont(font)
        self.pushButtonStart.setObjectName("pushButtonStart")
        self.pushButton_analyse_once = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_analyse_once.setGeometry(QtCore.QRect(348, 178, 141, 31))
        self.pushButton_analyse_once.setObjectName("pushButton_analyse_once")
        self.textBrowserOutput = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowserOutput.setGeometry(QtCore.QRect(8, 70, 621, 501))
        font = QtGui.QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        font.setStrikeOut(False)
        self.textBrowserOutput.setFont(font)
        self.textBrowserOutput.setObjectName("textBrowserOutput")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(646, 9, 111, 16))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(12)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.lineEditInput = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditInput.setGeometry(QtCore.QRect(8, 7, 471, 31))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.lineEditInput.setFont(font)
        self.lineEditInput.setText("")
        self.lineEditInput.setObjectName("lineEditInput")
        self.pushButtonStop = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonStop.setEnabled(False)
        self.pushButtonStop.setGeometry(QtCore.QRect(558, 7, 71, 31))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.pushButtonStop.setFont(font)
        self.pushButtonStop.setObjectName("pushButtonStop")
        self.labelState = QtWidgets.QLabel(self.centralwidget)
        self.labelState.setGeometry(QtCore.QRect(10, 47, 451, 16))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.labelState.setFont(font)
        self.labelState.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.labelState.setObjectName("labelState")
        self.labelSpeed = QtWidgets.QLabel(self.centralwidget)
        self.labelSpeed.setGeometry(QtCore.QRect(467, 46, 161, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.labelSpeed.setFont(font)
        self.labelSpeed.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.labelSpeed.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.labelSpeed.setObjectName("labelSpeed")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "LalalaScan"))
        self.pushButtonStart.setText(_translate("MainWindow", "开始扫描"))
        self.pushButton_analyse_once.setText(_translate("MainWindow", "Analyse Once"))
        self.textBrowserOutput.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Consolas\'; font-size:10pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'MS Shell Dlg 2\';\"><br /></p></body></html>"))
        self.label.setText(_translate("MainWindow", "插件"))
        self.pushButtonStop.setText(_translate("MainWindow", "停止扫描"))
        self.labelState.setText(_translate("MainWindow", "扫描信息: 准备就绪..."))
        self.labelSpeed.setText(_translate("MainWindow", "扫描速度: 0 / s"))
