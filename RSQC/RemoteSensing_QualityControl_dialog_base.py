# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'RemoteSensing_QualityControl_dialog_base.ui'
#
# Created: Mon Feb 19 14:43:15 2018
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

class Ui_RSQCDialogBase(object):
    def setupUi(self, RSQCDialogBase):
        RSQCDialogBase.setObjectName(_fromUtf8("RSQCDialogBase"))
        RSQCDialogBase.resize(493, 588)
        self.button_box = QtGui.QDialogButtonBox(RSQCDialogBase)
        self.button_box.setGeometry(QtCore.QRect(110, 550, 341, 32))
        self.button_box.setOrientation(QtCore.Qt.Horizontal)
        self.button_box.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.button_box.setObjectName(_fromUtf8("button_box"))
        self.tabWidget = QtGui.QTabWidget(RSQCDialogBase)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 481, 541))
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.lineEdit = QtGui.QLineEdit(self.tab)
        self.lineEdit.setGeometry(QtCore.QRect(10, 30, 371, 20))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.label = QtGui.QLabel(self.tab)
        self.label.setGeometry(QtCore.QRect(18, 7, 251, 16))
        self.label.setTextFormat(QtCore.Qt.PlainText)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_15 = QtGui.QLabel(self.tab)
        self.label_15.setGeometry(QtCore.QRect(18, 57, 161, 16))
        self.label_15.setObjectName(_fromUtf8("label_15"))
        self.pushButton_path = QtGui.QPushButton(self.tab)
        self.pushButton_path.setGeometry(QtCore.QRect(388, 27, 51, 23))
        self.pushButton_path.setObjectName(_fromUtf8("pushButton_path"))
        self.listWidget1 = QtGui.QListWidget(self.tab)
        self.listWidget1.setGeometry(QtCore.QRect(38, 127, 341, 221))
        self.listWidget1.setObjectName(_fromUtf8("listWidget1"))
        self.pushButton_index1 = QtGui.QPushButton(self.tab)
        self.pushButton_index1.setGeometry(QtCore.QRect(308, 77, 131, 23))
        self.pushButton_index1.setObjectName(_fromUtf8("pushButton_index1"))
        self.lineEdit_3 = QtGui.QLineEdit(self.tab)
        self.lineEdit_3.setGeometry(QtCore.QRect(8, 77, 281, 20))
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.label_27 = QtGui.QLabel(self.tab)
        self.label_27.setGeometry(QtCore.QRect(10, 110, 361, 16))
        self.label_27.setObjectName(_fromUtf8("label_27"))
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_PPC = QtGui.QWidget()
        self.tab_PPC.setObjectName(_fromUtf8("tab_PPC"))
        self.lineEditCamDir = QtGui.QLineEdit(self.tab_PPC)
        self.lineEditCamDir.setGeometry(QtCore.QRect(170, 110, 251, 21))
        self.lineEditCamDir.setObjectName(_fromUtf8("lineEditCamDir"))
        self.groupBox = QtGui.QGroupBox(self.tab_PPC)
        self.groupBox.setGeometry(QtCore.QRect(30, 150, 441, 311))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.checkBoxGSD = QtGui.QCheckBox(self.groupBox)
        self.checkBoxGSD.setGeometry(QtCore.QRect(20, 110, 111, 17))
        self.checkBoxGSD.setObjectName(_fromUtf8("checkBoxGSD"))
        self.checkBoxSun = QtGui.QCheckBox(self.groupBox)
        self.checkBoxSun.setGeometry(QtCore.QRect(20, 143, 101, 16))
        self.checkBoxSun.setObjectName(_fromUtf8("checkBoxSun"))
        self.lineEditGSD = QtGui.QLineEdit(self.groupBox)
        self.lineEditGSD.setGeometry(QtCore.QRect(180, 110, 51, 20))
        self.lineEditGSD.setText(_fromUtf8(""))
        self.lineEditGSD.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEditGSD.setObjectName(_fromUtf8("lineEditGSD"))
        self.labelGSD = QtGui.QLabel(self.groupBox)
        self.labelGSD.setGeometry(QtCore.QRect(240, 111, 61, 20))
        self.labelGSD.setObjectName(_fromUtf8("labelGSD"))
        self.lineEditSUN = QtGui.QLineEdit(self.groupBox)
        self.lineEditSUN.setGeometry(QtCore.QRect(180, 140, 51, 20))
        self.lineEditSUN.setText(_fromUtf8(""))
        self.lineEditSUN.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEditSUN.setObjectName(_fromUtf8("lineEditSUN"))
        self.labelSun = QtGui.QLabel(self.groupBox)
        self.labelSun.setGeometry(QtCore.QRect(240, 140, 71, 20))
        self.labelSun.setObjectName(_fromUtf8("labelSun"))
        self.checkBoxTilt = QtGui.QCheckBox(self.groupBox)
        self.checkBoxTilt.setGeometry(QtCore.QRect(20, 173, 70, 17))
        self.checkBoxTilt.setObjectName(_fromUtf8("checkBoxTilt"))
        self.labelTilt = QtGui.QLabel(self.groupBox)
        self.labelTilt.setGeometry(QtCore.QRect(240, 170, 61, 20))
        self.labelTilt.setObjectName(_fromUtf8("labelTilt"))
        self.lineEditTilt = QtGui.QLineEdit(self.groupBox)
        self.lineEditTilt.setGeometry(QtCore.QRect(180, 169, 51, 21))
        self.lineEditTilt.setText(_fromUtf8(""))
        self.lineEditTilt.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEditTilt.setObjectName(_fromUtf8("lineEditTilt"))
        self.lineEditRef = QtGui.QLineEdit(self.groupBox)
        self.lineEditRef.setGeometry(QtCore.QRect(170, 200, 161, 20))
        self.lineEditRef.setText(_fromUtf8(""))
        self.lineEditRef.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEditRef.setObjectName(_fromUtf8("lineEditRef"))
        self.checkBoxRef = QtGui.QCheckBox(self.groupBox)
        self.checkBoxRef.setGeometry(QtCore.QRect(20, 203, 151, 17))
        self.checkBoxRef.setObjectName(_fromUtf8("checkBoxRef"))
        self.checkBoxFile = QtGui.QCheckBox(self.groupBox)
        self.checkBoxFile.setGeometry(QtCore.QRect(20, 50, 411, 17))
        self.checkBoxFile.setObjectName(_fromUtf8("checkBoxFile"))
        self.checkBoxFormat = QtGui.QCheckBox(self.groupBox)
        self.checkBoxFormat.setGeometry(QtCore.QRect(20, 80, 401, 17))
        self.checkBoxFormat.setObjectName(_fromUtf8("checkBoxFormat"))
        self.checkBoxPic = QtGui.QCheckBox(self.groupBox)
        self.checkBoxPic.setGeometry(QtCore.QRect(20, 20, 381, 17))
        self.checkBoxPic.setObjectName(_fromUtf8("checkBoxPic"))
        self.checkBoxVoids = QtGui.QCheckBox(self.groupBox)
        self.checkBoxVoids.setGeometry(QtCore.QRect(20, 230, 231, 17))
        self.checkBoxVoids.setObjectName(_fromUtf8("checkBoxVoids"))
        self.labelCamDir = QtGui.QLabel(self.tab_PPC)
        self.labelCamDir.setGeometry(QtCore.QRect(40, 110, 151, 21))
        self.labelCamDir.setObjectName(_fromUtf8("labelCamDir"))
        self.groupBox_2 = QtGui.QGroupBox(self.tab_PPC)
        self.groupBox_2.setGeometry(QtCore.QRect(30, 10, 441, 91))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.inShapeAPPC = QtGui.QComboBox(self.groupBox_2)
        self.inShapeAPPC.setGeometry(QtCore.QRect(20, 20, 401, 22))
        self.inShapeAPPC.setObjectName(_fromUtf8("inShapeAPPC"))
        self.useSelectedAPPC = QtGui.QCheckBox(self.groupBox_2)
        self.useSelectedAPPC.setGeometry(QtCore.QRect(20, 60, 181, 17))
        self.useSelectedAPPC.setObjectName(_fromUtf8("useSelectedAPPC"))
        self.radioButtonPPC_ob = QtGui.QRadioButton(self.groupBox_2)
        self.radioButtonPPC_ob.setGeometry(QtCore.QRect(230, 60, 91, 17))
        self.radioButtonPPC_ob.setObjectName(_fromUtf8("radioButtonPPC_ob"))
        self.radioButtonPPC_Nadir = QtGui.QRadioButton(self.groupBox_2)
        self.radioButtonPPC_Nadir.setGeometry(QtCore.QRect(340, 60, 82, 17))
        self.radioButtonPPC_Nadir.setObjectName(_fromUtf8("radioButtonPPC_Nadir"))
        self.pushButton_InputPPC = QtGui.QPushButton(self.tab_PPC)
        self.pushButton_InputPPC.setGeometry(QtCore.QRect(440, 110, 31, 21))
        self.pushButton_InputPPC.setObjectName(_fromUtf8("pushButton_InputPPC"))
        self.tabWidget.addTab(self.tab_PPC, _fromUtf8(""))
        self.tab_DB = QtGui.QWidget()
        self.tab_DB.setObjectName(_fromUtf8("tab_DB"))
        self.groupBox_7 = QtGui.QGroupBox(self.tab_DB)
        self.groupBox_7.setGeometry(QtCore.QRect(30, 230, 441, 111))
        self.groupBox_7.setObjectName(_fromUtf8("groupBox_7"))
        self.inShapeDB = QtGui.QComboBox(self.groupBox_7)
        self.inShapeDB.setGeometry(QtCore.QRect(20, 20, 401, 22))
        self.inShapeDB.setObjectName(_fromUtf8("inShapeDB"))
        self.useSelectedDB = QtGui.QCheckBox(self.groupBox_7)
        self.useSelectedDB.setGeometry(QtCore.QRect(10, 60, 221, 17))
        self.useSelectedDB.setObjectName(_fromUtf8("useSelectedDB"))
        self.radioButtonDB_ob = QtGui.QRadioButton(self.groupBox_7)
        self.radioButtonDB_ob.setGeometry(QtCore.QRect(260, 60, 201, 17))
        self.radioButtonDB_ob.setObjectName(_fromUtf8("radioButtonDB_ob"))
        self.radioButtonDB_Nadir = QtGui.QRadioButton(self.groupBox_7)
        self.radioButtonDB_Nadir.setGeometry(QtCore.QRect(260, 80, 201, 17))
        self.radioButtonDB_Nadir.setObjectName(_fromUtf8("radioButtonDB_Nadir"))
        self.OverwriteDB = QtGui.QCheckBox(self.tab_DB)
        self.OverwriteDB.setGeometry(QtCore.QRect(40, 350, 181, 17))
        self.OverwriteDB.setObjectName(_fromUtf8("OverwriteDB"))
        self.groupBoxCredentials = QtGui.QGroupBox(self.tab_DB)
        self.groupBoxCredentials.setGeometry(QtCore.QRect(30, 20, 441, 181))
        self.groupBoxCredentials.setObjectName(_fromUtf8("groupBoxCredentials"))
        self.db_name = QtGui.QLineEdit(self.groupBoxCredentials)
        self.db_name.setGeometry(QtCore.QRect(100, 30, 261, 20))
        self.db_name.setObjectName(_fromUtf8("db_name"))
        self.label_5 = QtGui.QLabel(self.groupBoxCredentials)
        self.label_5.setGeometry(QtCore.QRect(20, 30, 101, 16))
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.db_host = QtGui.QLineEdit(self.groupBoxCredentials)
        self.db_host.setGeometry(QtCore.QRect(100, 60, 261, 20))
        self.db_host.setObjectName(_fromUtf8("db_host"))
        self.label_6 = QtGui.QLabel(self.groupBoxCredentials)
        self.label_6.setGeometry(QtCore.QRect(20, 60, 101, 16))
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.db_user = QtGui.QLineEdit(self.groupBoxCredentials)
        self.db_user.setGeometry(QtCore.QRect(100, 90, 261, 20))
        self.db_user.setObjectName(_fromUtf8("db_user"))
        self.label_7 = QtGui.QLabel(self.groupBoxCredentials)
        self.label_7.setGeometry(QtCore.QRect(20, 90, 101, 16))
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.db_password = QtGui.QLineEdit(self.groupBoxCredentials)
        self.db_password.setGeometry(QtCore.QRect(100, 120, 261, 20))
        self.db_password.setObjectName(_fromUtf8("db_password"))
        self.label_8 = QtGui.QLabel(self.groupBoxCredentials)
        self.label_8.setGeometry(QtCore.QRect(20, 120, 101, 16))
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.db_port = QtGui.QLineEdit(self.groupBoxCredentials)
        self.db_port.setGeometry(QtCore.QRect(100, 150, 261, 20))
        self.db_port.setObjectName(_fromUtf8("db_port"))
        self.label_9 = QtGui.QLabel(self.groupBoxCredentials)
        self.label_9.setGeometry(QtCore.QRect(20, 150, 101, 16))
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.tabWidget.addTab(self.tab_DB, _fromUtf8(""))
        self.tab_Disk = QtGui.QWidget()
        self.tab_Disk.setObjectName(_fromUtf8("tab_Disk"))
        self.groupBox_4 = QtGui.QGroupBox(self.tab_Disk)
        self.groupBox_4.setGeometry(QtCore.QRect(30, 10, 441, 441))
        self.groupBox_4.setObjectName(_fromUtf8("groupBox_4"))
        self.textEdit = QtGui.QTextEdit(self.groupBox_4)
        self.textEdit.setGeometry(QtCore.QRect(10, 20, 421, 401))
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.tabWidget.addTab(self.tab_Disk, _fromUtf8(""))
        self.tab_DBQC = QtGui.QWidget()
        self.tab_DBQC.setObjectName(_fromUtf8("tab_DBQC"))
        self.labelImageDir_2 = QtGui.QLabel(self.tab_DBQC)
        self.labelImageDir_2.setGeometry(QtCore.QRect(40, 340, 101, 16))
        self.labelImageDir_2.setObjectName(_fromUtf8("labelImageDir_2"))
        self.lineEditDBImageDir = QtGui.QLineEdit(self.tab_DBQC)
        self.lineEditDBImageDir.setGeometry(QtCore.QRect(150, 340, 261, 21))
        self.lineEditDBImageDir.setText(_fromUtf8(""))
        self.lineEditDBImageDir.setObjectName(_fromUtf8("lineEditDBImageDir"))
        self.pushButton_InputDB = QtGui.QPushButton(self.tab_DBQC)
        self.pushButton_InputDB.setGeometry(QtCore.QRect(420, 340, 31, 21))
        self.pushButton_InputDB.setObjectName(_fromUtf8("pushButton_InputDB"))
        self.groupBox_3 = QtGui.QGroupBox(self.tab_DBQC)
        self.groupBox_3.setGeometry(QtCore.QRect(30, 230, 441, 91))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.inShapeAImage = QtGui.QComboBox(self.groupBox_3)
        self.inShapeAImage.setGeometry(QtCore.QRect(20, 20, 401, 22))
        self.inShapeAImage.setObjectName(_fromUtf8("inShapeAImage"))
        self.radioButtonDBQC_ob = QtGui.QRadioButton(self.groupBox_3)
        self.radioButtonDBQC_ob.setGeometry(QtCore.QRect(240, 60, 91, 17))
        self.radioButtonDBQC_ob.setObjectName(_fromUtf8("radioButtonDBQC_ob"))
        self.radioButtonDBQC_Nadir = QtGui.QRadioButton(self.groupBox_3)
        self.radioButtonDBQC_Nadir.setGeometry(QtCore.QRect(350, 60, 82, 17))
        self.radioButtonDBQC_Nadir.setObjectName(_fromUtf8("radioButtonDBQC_Nadir"))
        self.groupBoxCredentials_2 = QtGui.QGroupBox(self.tab_DBQC)
        self.groupBoxCredentials_2.setGeometry(QtCore.QRect(30, 20, 441, 181))
        self.groupBoxCredentials_2.setObjectName(_fromUtf8("groupBoxCredentials_2"))
        self.db_name_2 = QtGui.QLineEdit(self.groupBoxCredentials_2)
        self.db_name_2.setGeometry(QtCore.QRect(100, 30, 321, 20))
        self.db_name_2.setObjectName(_fromUtf8("db_name_2"))
        self.label_10 = QtGui.QLabel(self.groupBoxCredentials_2)
        self.label_10.setGeometry(QtCore.QRect(20, 30, 101, 16))
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.db_host_2 = QtGui.QLineEdit(self.groupBoxCredentials_2)
        self.db_host_2.setGeometry(QtCore.QRect(100, 60, 321, 20))
        self.db_host_2.setObjectName(_fromUtf8("db_host_2"))
        self.label_11 = QtGui.QLabel(self.groupBoxCredentials_2)
        self.label_11.setGeometry(QtCore.QRect(20, 60, 101, 16))
        self.label_11.setObjectName(_fromUtf8("label_11"))
        self.db_user_2 = QtGui.QLineEdit(self.groupBoxCredentials_2)
        self.db_user_2.setGeometry(QtCore.QRect(100, 90, 321, 20))
        self.db_user_2.setObjectName(_fromUtf8("db_user_2"))
        self.label_12 = QtGui.QLabel(self.groupBoxCredentials_2)
        self.label_12.setGeometry(QtCore.QRect(20, 90, 101, 16))
        self.label_12.setObjectName(_fromUtf8("label_12"))
        self.db_password_2 = QtGui.QLineEdit(self.groupBoxCredentials_2)
        self.db_password_2.setGeometry(QtCore.QRect(100, 120, 321, 20))
        self.db_password_2.setObjectName(_fromUtf8("db_password_2"))
        self.label_13 = QtGui.QLabel(self.groupBoxCredentials_2)
        self.label_13.setGeometry(QtCore.QRect(20, 120, 101, 16))
        self.label_13.setObjectName(_fromUtf8("label_13"))
        self.db_port_2 = QtGui.QLineEdit(self.groupBoxCredentials_2)
        self.db_port_2.setGeometry(QtCore.QRect(100, 150, 321, 20))
        self.db_port_2.setObjectName(_fromUtf8("db_port_2"))
        self.label_14 = QtGui.QLabel(self.groupBoxCredentials_2)
        self.label_14.setGeometry(QtCore.QRect(20, 150, 101, 16))
        self.label_14.setObjectName(_fromUtf8("label_14"))
        self.tabWidget.addTab(self.tab_DBQC, _fromUtf8(""))

        self.retranslateUi(RSQCDialogBase)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("rejected()")), RSQCDialogBase.reject)
        QtCore.QObject.connect(self.button_box, QtCore.SIGNAL(_fromUtf8("accepted()")), RSQCDialogBase.accept)
        QtCore.QMetaObject.connectSlotsByName(RSQCDialogBase)

    def retranslateUi(self, RSQCDialogBase):
        RSQCDialogBase.setWindowTitle(_translate("RSQCDialogBase", "RS QC", None))
        self.label.setText(_translate("RSQCDialogBase", "Disc or folder to index:", None))
        self.label_15.setText(_translate("RSQCDialogBase", "Index name in DB (index2018):", None))
        self.pushButton_path.setText(_translate("RSQCDialogBase", "...", None))
        self.pushButton_index1.setText(_translate("RSQCDialogBase", "Get privious indexes", None))
        self.label_27.setText(_translate("RSQCDialogBase", "  ", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("RSQCDialogBase", "#1 Index", None))
        self.groupBox.setTitle(_translate("RSQCDialogBase", "To be checked", None))
        self.checkBoxGSD.setText(_translate("RSQCDialogBase", "GSD", None))
        self.checkBoxSun.setText(_translate("RSQCDialogBase", "Sun angle", None))
        self.labelGSD.setText(_translate("RSQCDialogBase", "Meters", None))
        self.labelSun.setText(_translate("RSQCDialogBase", "Degrees", None))
        self.checkBoxTilt.setText(_translate("RSQCDialogBase", "Tilt", None))
        self.labelTilt.setText(_translate("RSQCDialogBase", "Degrees", None))
        self.checkBoxRef.setText(_translate("RSQCDialogBase", "Reference system:", None))
        self.checkBoxFile.setText(_translate("RSQCDialogBase", "File format conforms to SDFE Standard", None))
        self.checkBoxFormat.setText(_translate("RSQCDialogBase", "Feature format conforms to SDFE Standard", None))
        self.checkBoxPic.setText(_translate("RSQCDialogBase", "Check image naming", None))
        self.checkBoxVoids.setText(_translate("RSQCDialogBase", "Footprint Void Check", None))
        self.labelCamDir.setText(_translate("RSQCDialogBase", "Path to camera dir:", None))
        self.groupBox_2.setTitle(_translate("RSQCDialogBase", "PPC or footprint file", None))
        self.useSelectedAPPC.setText(_translate("RSQCDialogBase", "Use only selected features", None))
        self.radioButtonPPC_ob.setText(_translate("RSQCDialogBase", "Oblique", None))
        self.radioButtonPPC_Nadir.setText(_translate("RSQCDialogBase", "Nadir", None))
        self.pushButton_InputPPC.setText(_translate("RSQCDialogBase", "...", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_PPC), _translate("RSQCDialogBase", "#2 - Footprint/PPC", None))
        self.groupBox_7.setTitle(_translate("RSQCDialogBase", "Shapefile to upload to DB", None))
        self.useSelectedDB.setText(_translate("RSQCDialogBase", "Use only selected features", None))
        self.radioButtonDB_ob.setText(_translate("RSQCDialogBase", "Oblique ( footprints2018)", None))
        self.radioButtonDB_Nadir.setText(_translate("RSQCDialogBase", "Nadir ( ppc2018)", None))
        self.OverwriteDB.setText(_translate("RSQCDialogBase", "Overwrite existing DB files", None))
        self.groupBoxCredentials.setTitle(_translate("RSQCDialogBase", "Database credentials", None))
        self.label_5.setText(_translate("RSQCDialogBase", "Database", None))
        self.label_6.setText(_translate("RSQCDialogBase", "Hostname", None))
        self.label_7.setText(_translate("RSQCDialogBase", "Username", None))
        self.label_8.setText(_translate("RSQCDialogBase", "Password", None))
        self.label_9.setText(_translate("RSQCDialogBase", "Port", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_DB), _translate("RSQCDialogBase", "#3 - DB upload", None))
        self.groupBox_4.setTitle(_translate("RSQCDialogBase", "Path to image dir:", None))
        self.textEdit.setHtml(_translate("RSQCDialogBase", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">####  Only for SDFE!  ####</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">     </span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">###INFO###</span></p>\n"
"<p align=\"center\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">1. Brug notepad++ til at åbne filen &quot;CheckImages.bat&quot; som ligger i \'C:/temp/imageQC/\' på arbejds PC\'erne</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">2. Rediger filen, så den passet til den aktuelle disc:</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:7pt;\">################################################</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:7pt;\">##   python RunAllFilesInDir.py -i </span><span style=\" font-size:7pt; font-weight:600;\">J:\\Block_81_07\\Image_JPEG\\</span><span style=\" font-size:7pt;\"> -s 1  ##</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:7pt;\">##           |       |       |      |       |       |               ##</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:7pt;\">##           v      v       v     v      v       v           ##</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:7pt;\">##  python RunAllFilesInDir.py -i </span><span style=\" font-size:7pt; font-weight:600;\">H:\\Block_83_30\\Image_TIFF\\</span><span style=\" font-size:7pt;\"> -s 1  ##</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:7pt;\">################################################</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:7pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">3. Kør til slut bat-filen fra en Osgeo4w shell.</span></p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:8pt;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:8pt;\">4. Når scriptet er færdig er #3 slut!</span></p></body></html>", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_Disk), _translate("RSQCDialogBase", "#4 - Disk", None))
        self.labelImageDir_2.setText(_translate("RSQCDialogBase", "Image Dir Path:", None))
        self.pushButton_InputDB.setText(_translate("RSQCDialogBase", "...", None))
        self.groupBox_3.setTitle(_translate("RSQCDialogBase", "PPC or footprint Database", None))
        self.radioButtonDBQC_ob.setText(_translate("RSQCDialogBase", "Oblique", None))
        self.radioButtonDBQC_Nadir.setText(_translate("RSQCDialogBase", "Nadir", None))
        self.groupBoxCredentials_2.setTitle(_translate("RSQCDialogBase", "Database credentials", None))
        self.label_10.setText(_translate("RSQCDialogBase", "Database", None))
        self.label_11.setText(_translate("RSQCDialogBase", "Hostname", None))
        self.label_12.setText(_translate("RSQCDialogBase", "Username", None))
        self.label_13.setText(_translate("RSQCDialogBase", "Password", None))
        self.label_14.setText(_translate("RSQCDialogBase", "Port", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_DBQC), _translate("RSQCDialogBase", "#5 - DB QC", None))
