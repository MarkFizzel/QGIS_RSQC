# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'progressbar.ui'
#
# Created: Fri Dec 22 10:32:59 2017
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(440, 233)
        self.progressBar = QtGui.QProgressBar(Dialog)
        self.progressBar.setGeometry(QtCore.QRect(9, 106, 421, 21))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.pgr_label = QtGui.QLabel(Dialog)
        self.pgr_label.setGeometry(QtCore.QRect(60, 50, 291, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.pgr_label.setFont(font)
        self.pgr_label.setText(_fromUtf8(""))
        self.pgr_label.setAlignment(QtCore.Qt.AlignCenter)
        self.pgr_label.setObjectName(_fromUtf8("pgr_label"))
        self.pushButton_cancel = QtGui.QPushButton(Dialog)
        self.pushButton_cancel.setGeometry(QtCore.QRect(340, 180, 75, 23))
        self.pushButton_cancel.setObjectName(_fromUtf8("pushButton_cancel"))
        self.pushButton_start = QtGui.QPushButton(Dialog)
        self.pushButton_start.setGeometry(QtCore.QRect(250, 180, 75, 23))
        self.pushButton_start.setObjectName(_fromUtf8("pushButton_start"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Progress", None))
        self.pushButton_cancel.setText(_translate("Dialog", "Cancel", None))
        self.pushButton_start.setText(_translate("Dialog", "Start", None))

