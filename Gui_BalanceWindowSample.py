# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Gui_BalanceWindowSample.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_BalanceWindow(object):
    def setupUi(self, BalanceWindow):
        BalanceWindow.setObjectName("BalanceWindow")
        BalanceWindow.setWindowModality(QtCore.Qt.NonModal)
        BalanceWindow.resize(315, 357)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(BalanceWindow.sizePolicy().hasHeightForWidth())
        BalanceWindow.setSizePolicy(sizePolicy)
        BalanceWindow.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("img/Logo.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        BalanceWindow.setWindowIcon(icon)
        BalanceWindow.setWhatsThis("")
        BalanceWindow.setStyleSheet("background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0.983, y2:0.227273, stop:0 rgba(227, 91, 0, 255), stop:1 rgba(255, 255, 255, 255));")
        BalanceWindow.setModal(False)
        self.label_userBalances = QtWidgets.QLabel(BalanceWindow)
        self.label_userBalances.setEnabled(True)
        self.label_userBalances.setGeometry(QtCore.QRect(89, 6, 140, 20))
        self.label_userBalances.setStyleSheet("background-color:0,0,0,10")
        self.label_userBalances.setAlignment(QtCore.Qt.AlignCenter)
        self.label_userBalances.setObjectName("label_userBalances")
        self.tableWidget_balanceTable = QtWidgets.QTableWidget(BalanceWindow)
        self.tableWidget_balanceTable.setEnabled(True)
        self.tableWidget_balanceTable.setGeometry(QtCore.QRect(24, 30, 271, 261))
        self.tableWidget_balanceTable.setStyleSheet("background-color:0,0,0,10")
        self.tableWidget_balanceTable.setAlternatingRowColors(True)
        self.tableWidget_balanceTable.setRowCount(10)
        self.tableWidget_balanceTable.setObjectName("tableWidget_balanceTable")
        self.tableWidget_balanceTable.setColumnCount(2)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget_balanceTable.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.tableWidget_balanceTable.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setFlags(QtCore.Qt.ItemIsSelectable|QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
        self.tableWidget_balanceTable.setItem(0, 0, item)
        self.tableWidget_balanceTable.horizontalHeader().setDefaultSectionSize(72)
        self.tableWidget_balanceTable.horizontalHeader().setStretchLastSection(True)
        self.tableWidget_balanceTable.verticalHeader().setVisible(False)
        self.tableWidget_balanceTable.verticalHeader().setCascadingSectionResizes(False)
        self.tableWidget_balanceTable.verticalHeader().setDefaultSectionSize(23)
        self.tableWidget_balanceTable.verticalHeader().setMinimumSectionSize(3)
        self.tableWidget_balanceTable.verticalHeader().setSortIndicatorShown(True)
        self.tableWidget_balanceTable.verticalHeader().setStretchLastSection(True)
        self.checkBox_circularRefreshBalance = QtWidgets.QCheckBox(BalanceWindow)
        self.checkBox_circularRefreshBalance.setGeometry(QtCore.QRect(158, 322, 151, 17))
        self.checkBox_circularRefreshBalance.setStyleSheet("background-color:0,0,0,10")
        self.checkBox_circularRefreshBalance.setObjectName("checkBox_circularRefreshBalance")
        self.pushButton_EnableBalanceRefreshTime = QtWidgets.QPushButton(BalanceWindow)
        self.pushButton_EnableBalanceRefreshTime.setEnabled(False)
        self.pushButton_EnableBalanceRefreshTime.setGeometry(QtCore.QRect(60, 319, 75, 23))
        self.pushButton_EnableBalanceRefreshTime.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.pushButton_EnableBalanceRefreshTime.setObjectName("pushButton_EnableBalanceRefreshTime")
        self.label_balanceRefreshTime = QtWidgets.QLabel(BalanceWindow)
        self.label_balanceRefreshTime.setEnabled(False)
        self.label_balanceRefreshTime.setGeometry(QtCore.QRect(10, 299, 101, 16))
        self.label_balanceRefreshTime.setStyleSheet("background-color:0,0,0,10")
        self.label_balanceRefreshTime.setObjectName("label_balanceRefreshTime")
        self.spinBox_balanceRefreshTime = QtWidgets.QSpinBox(BalanceWindow)
        self.spinBox_balanceRefreshTime.setEnabled(False)
        self.spinBox_balanceRefreshTime.setGeometry(QtCore.QRect(10, 319, 42, 22))
        self.spinBox_balanceRefreshTime.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.spinBox_balanceRefreshTime.setMaximum(999)
        self.spinBox_balanceRefreshTime.setProperty("value", 3)
        self.spinBox_balanceRefreshTime.setDisplayIntegerBase(10)
        self.spinBox_balanceRefreshTime.setObjectName("spinBox_balanceRefreshTime")

        self.retranslateUi(BalanceWindow)
        QtCore.QMetaObject.connectSlotsByName(BalanceWindow)

    def retranslateUi(self, BalanceWindow):
        _translate = QtCore.QCoreApplication.translate
        BalanceWindow.setWindowTitle(_translate("BalanceWindow", "Балансы пользователя"))
        self.label_userBalances.setText(_translate("BalanceWindow", "<html><head/><body><p><span style=\" font-weight:600;\">Балансы аккаунта</span></p></body></html>"))
        item = self.tableWidget_balanceTable.horizontalHeaderItem(0)
        item.setText(_translate("BalanceWindow", "Валюта"))
        item = self.tableWidget_balanceTable.horizontalHeaderItem(1)
        item.setText(_translate("BalanceWindow", "Баланс"))
        __sortingEnabled = self.tableWidget_balanceTable.isSortingEnabled()
        self.tableWidget_balanceTable.setSortingEnabled(False)
        self.tableWidget_balanceTable.setSortingEnabled(__sortingEnabled)
        self.checkBox_circularRefreshBalance.setText(_translate("BalanceWindow", "Циклическое обновление"))
        self.pushButton_EnableBalanceRefreshTime.setText(_translate("BalanceWindow", "Установить"))
        self.label_balanceRefreshTime.setText(_translate("BalanceWindow", "<html><head/><body><p>Время обновления</p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    BalanceWindow = QtWidgets.QDialog()
    ui = Ui_BalanceWindow()
    ui.setupUi(BalanceWindow)
    BalanceWindow.show()
    sys.exit(app.exec_())
