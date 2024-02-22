from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5.QtCore import QThread

from Gui_CryptoMonkeySample import Ui_CryptoMonkey
from Gui_ApiKeysInputWindowSample import Ui_Dialog_apiKeysInput
from Gui_BalanceWindowSample import Ui_BalanceWindow
from Gui_TradeSettingsWindowSample import Ui_TradeSettingsWindow

from ProcessingCore import Settings
from ProcessingCore import ParsThread
from ProcessingCore import ProcessThread

from TelegramBot import TelegramBot

import os
import sys
import logging
import json

## Принудительное переключение рабочей директории ##
file_path = os.path.realpath(__file__).rsplit('\\', 1)[0]
os.chdir(file_path)

def init_logger(name):
    logger = logging.getLogger(name)
    FORMAT = "%(asctime)s -- %(name)s -- %(lineno)s -- %(levelname)s -- %(message)s"
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler()
    sh.setFormatter(logging.Formatter(FORMAT))
    sh.setLevel(logging.DEBUG)
    fh = logging.FileHandler(filename="Logs.txt", encoding="UTF-8")
    fh.setFormatter(logging.Formatter(FORMAT))
    fh.setLevel(logging.DEBUG)
    logger.addHandler(sh)
    logger.addHandler(fh)
    logger.debug('logger was initialized')

init_logger('CryptoMonkey')
logger = logging.getLogger('CryptoMonkey.CryptoMonkeyGui')


class CryptoMonkeyGui(QMainWindow):
    """Класс-обертка для основного окна приложения"""

    path = file_path  # директория, из которой запускается программа
    selectedQuotationCoin = 'XRP'
    selectedBasicCoin = 'USDT'
    circularRefreshOn = False
    balanceAutoRefreshOn = False
    balanceWinOpen = False
    refreshTime = 0
    startParsButtonClicked = False
    infoUnfilledRowNumber = 0
    ordersUnfilledRowNumber = 0
    unfilledDiagRowNum = 0
    keysPath = 'D:\\python\\projects'  # путь к файлу с ключами от аккаунта пользователя
    openOrdersListPath = path + '\\open_orders.txt'  # путь к файлу с перечнем открытых ордеров
    imitationMode = False

    def __init__(self):
        super(CryptoMonkeyGui, self).__init__()
        self.ui = Ui_CryptoMonkey()
        self.ui.setupUi(self)
        self.add_guiFunctions()

        self.startOrdersInfoThread()
        ParsThread.keysPath = self.keysPath
        ProcessThread.keysPath = self.keysPath

    ### Методы обработки действий пользователя ###

    def add_guiFunctions(self) -> None:
        """Добавление функций обработки действий пользователя в главном окне приложения"""

        self.ui.pushButton_apiKeysLoad.clicked.connect(self.openKeysInputWindow)
        self.ui.pushButton_enableCoinChoice.clicked.connect(self.enableCoinChoice)
        self.ui.pushButton_EnableRefreshTime.clicked.connect(self.enableRefreshTime)
        self.ui.checkBox_circularRefresh.clicked.connect(self.circularRefreshSwitcher)
        self.ui.checkBox_allCoinsRender.clicked.connect(self.allCoinsRenderSwitcher)
        self.ui.pushButton_loadSiteData.clicked.connect(self.startParsingThread)
        self.ui.pushButton_coinSearch.clicked.connect(self.startCoinSearch)
        self.ui.pushButton_addNewCoin.clicked.connect(self.addNewCoin)
        self.ui.pushButton_deleteCoin.clicked.connect(self.deleteCoin)
        self.ui.checkBox_tgBotOn.clicked.connect(self.enableTelegramBot)

        self.ui.pushButton_getBalances.clicked.connect(self.openBalanceWindow)
        self.ui.pushButton_placeOrder.clicked.connect(self.startPlaceOrderThread)
        self.ui.pushButton_cancelOrder.clicked.connect(self.startCancelingOrder)
        self.ui.pushButton_getOpenOrdersInfo.clicked.connect(self.startOrdersInfoThread)
        self.ui.pushButton_cryptoBotStart.clicked.connect(self.openAutoTradeSetWindow)

        self.ui.checkBox_enableImitatitonTrade.clicked.connect(self.enableImitationMode)

    def enableTelegramBot(self) -> None:
        """Включение телеграм-бота"""

        if self.ui.checkBox_tgBotOn.isChecked():
            TelegramBot.botState(True)
        else:
            TelegramBot.botState(False)

    def enableCoinChoice(self) -> None:
        """Применение настроек поиска валют"""

        self.selectedQuotationCoin = self.ui.comboBox_quotationCoin.currentText()
        CryptoMonkeyGui.selectedBasicCoin = self.ui.comboBox_basicCoin.currentText()
        ParsThread.baseCoin = self.ui.comboBox_basicCoin.currentText()

    def enableRefreshTime(self) -> None:
        CryptoMonkeyGui.refreshTime = self.ui.spinBox_refreshTime.value()
        ParsThread.refreshTime = self.ui.spinBox_refreshTime.value()

    def enableTradeSettings(self, availableExchanges: list) -> None:
        """Активация настроек торговли после ввода и сохранения ключей API"""

        if availableExchanges:
            enabledItem = None
            self.ui.label_exchangeType.setDisabled(False)
            self.ui.label_dealType.setDisabled(False)
            self.ui.label_orderType.setDisabled(False)
            self.ui.label_buyAmount.setDisabled(False)
            self.ui.label_currencyPrice.setDisabled(False)
            self.ui.label_tradeQuotCoin.setDisabled(False)
            self.ui.label_tradeBaseCoin.setDisabled(False)
            self.ui.comboBox_exchangeType.setDisabled(False)
            self.ui.comboBox_dealType.setDisabled(False)
            self.ui.comboBox_orderType.setDisabled(False)
            self.ui.spinBox_buyAmount.setDisabled(False)
            self.ui.doubleSpinBox_currencyPrice.setDisabled(False)
            self.ui.pushButton_placeOrder.setDisabled(False)
            self.ui.pushButton_cancelOrder.setDisabled(False)
            self.ui.pushButton_getOpenOrdersInfo.setDisabled(False)
            self.ui.pushButton_getBalances.setDisabled(False)
            self.ui.comboBox_tradeQuotCoin.setDisabled(False)
            self.ui.comboBox_tradeBaseCoin.setDisabled(False)
            self.ui.textBrowser_tradeImitationBox.setDisabled(False)
            self.ui.checkBox_enableImitatitonTrade.setDisabled(False)
            self.ui.pushButton_cryptoBotStart.setDisabled(False)

            model = self.ui.comboBox_exchangeType.model()
            for itemNum in range(self.ui.comboBox_exchangeType.count()):
                if not self.ui.comboBox_exchangeType.itemText(itemNum) in availableExchanges:
                    model.item(itemNum).setEnabled(False)
                else:
                    model.item(itemNum).setEnabled(True)
                    enabledItem = itemNum
            if not model.item(self.ui.comboBox_exchangeType.currentIndex()).isEnabled() and enabledItem != None:
                self.ui.comboBox_exchangeType.setCurrentIndex(enabledItem)

        else:
            self.ui.label_exchangeType.setDisabled(True)
            self.ui.label_dealType.setDisabled(True)
            self.ui.label_orderType.setDisabled(True)
            self.ui.label_buyAmount.setDisabled(True)
            self.ui.label_currencyPrice.setDisabled(True)
            self.ui.comboBox_exchangeType.setDisabled(True)
            self.ui.comboBox_dealType.setDisabled(True)
            self.ui.comboBox_orderType.setDisabled(True)
            self.ui.spinBox_buyAmount.setDisabled(True)
            self.ui.doubleSpinBox_currencyPrice.setDisabled(True)
            self.ui.pushButton_placeOrder.setDisabled(True)
            self.ui.pushButton_cancelOrder.setDisabled(True)
            self.ui.pushButton_getOpenOrdersInfo.setDisabled(True)
            self.ui.pushButton_getBalances.setDisabled(True)
            self.ui.comboBox_tradeQuotCoin.setDisabled(True)
            self.ui.comboBox_tradeBaseCoin.setDisabled(True)
            self.ui.textBrowser_tradeImitationBox.setDisabled(True)
            self.ui.checkBox_enableImitatitonTrade.setDisabled(True)
            self.ui.pushButton_cryptoBotStart.setDisabled(True)

    def circularRefreshSwitcher(self) -> None:
        """Включение циклического парсинга и обновления информационных данных по выбранным биржам и валютам"""

        if self.ui.checkBox_circularRefresh.isChecked():
            self.ui.label_refreshTime.setDisabled(False)
            self.ui.spinBox_refreshTime.setDisabled(False)
            self.ui.pushButton_EnableRefreshTime.setDisabled(False)
            CryptoMonkeyGui.circularRefreshOn = True
            CryptoMonkeyGui.refreshTime = self.ui.spinBox_refreshTime.value()
            ParsThread.refreshTime = self.ui.spinBox_refreshTime.value()
            ParsThread.circularRefreshOn = True

            if self.startParsButtonClicked:
                self.startParsingThread()
        else:
            self.ui.label_refreshTime.setDisabled(True)
            self.ui.spinBox_refreshTime.setDisabled(True)
            self.ui.pushButton_EnableRefreshTime.setDisabled(True)
            CryptoMonkeyGui.circularRefreshOn = False
            ParsThread.circularRefreshOn = False

    def allCoinsRenderSwitcher(self) -> None:
        """Включение поиска и отображения котировок по всем валютам выбранных бирж"""

        if self.ui.checkBox_allCoinsRender.isChecked():
            self.ui.label_coinSearch.setDisabled(True)
            self.ui.lineEdit_coinSearch.setDisabled(True)
            self.ui.pushButton_coinSearch.setDisabled(True)
            self.ui.comboBox_quotationCoin.setDisabled(True)
            self.ui.label_quotationCoin.setDisabled(True)
            self.ui.pushButton_addNewCoin.setDisabled(True)
            self.ui.pushButton_deleteCoin.setDisabled(True)
        else:
            self.ui.label_coinSearch.setDisabled(False)
            self.ui.lineEdit_coinSearch.setDisabled(False)
            self.ui.pushButton_coinSearch.setDisabled(False)
            self.ui.comboBox_quotationCoin.setDisabled(False)
            self.ui.label_quotationCoin.setDisabled(False)
            self.ui.pushButton_addNewCoin.setDisabled(False)
            self.ui.pushButton_deleteCoin.setDisabled(False)

    def startCoinSearch(self) -> None:
        """Запуск поиска котировок и их отображения"""

        enteredCoinName = self.ui.lineEdit_coinSearch.text()
        try:
            for row in range(self.ui.comboBox_quotationCoin.count()):
                cboxCoinName = self.ui.comboBox_quotationCoin.itemText(row).lower().replace(' ', '').replace('.', '')
                if enteredCoinName.lower().replace(' ', '').replace('.', '') in cboxCoinName or \
                        cboxCoinName in enteredCoinName.lower().replace(' ', '').replace('.', ''):
                    self.ui.comboBox_quotationCoin.setCurrentIndex(row)
                    self.selectedQuotationCoin = self.ui.comboBox_quotationCoin.currentText()
                    return
            self.ui.comboBox_quotationCoin.setCurrentText(enteredCoinName)
        except Exception as ex:
            logger.error(ex)

    def addNewCoin(self) -> None:
        """Добавление новой котируемой валюты в список валют для поиска"""

        try:
            j = 0
            for symbol in self.ui.lineEdit_coinSearch.text():
                if (symbol != '') and (symbol != ' '):
                    self.ui.comboBox_quotationCoin.addItem(self.ui.lineEdit_coinSearch.text()[j:])
                    self.ui.comboBox_quotationCoin.setCurrentIndex(self.ui.comboBox_quotationCoin.count()-1)

                    centralCoinModel = self.ui.comboBox_quotationCoin.model()
                    self.ui.comboBox_tradeQuotCoin.clear()
                    self.ui.comboBox_tradeQuotCoin.setModel(centralCoinModel)

                    return
                j += 1
            self.ui.lineEdit_coinSearch.clear()

        except Exception as ex:
            logger.error(ex)

    def deleteCoin(self) -> None:
        """Удаление выбранной котируемой валюты из списка валют для поиска"""

        self.model = self.ui.comboBox_quotationCoin.model()
        self.model.removeRow(self.ui.comboBox_quotationCoin.currentIndex())
        self.ui.comboBox_quotationCoin.setCurrentIndex(0)

    def openKeysInputWindow(self) -> None:
        """Открытие окна ввода ключей API личного кабинета пользователя"""

        try:
            self.keysInputWindow = KeysInputWindow(self)
            self.keysInputWindow.show()
            self.keysInputWindow.exec_()
        except Exception as ex:
            logger.error(ex)

    def openBalanceWindow(self) -> None:
        """Открытие окна отображения балансов личного кабинета пользователя"""

        try:
            if not CryptoMonkeyGui.balanceWinOpen:
                self.ui.pushButton_getBalances.setDisabled(True)
                CryptoMonkeyGui.balanceWinOpen = True
                self.balanceWindow = BalanceWindow(self)
                self.balanceWindow.show()
                self.balanceWindow.exec_()
            elif not CryptoMonkeyGui.balanceAutoRefreshOn and CryptoMonkeyGui.balanceWinOpen:
                self.ui.pushButton_getBalances.setDisabled(True)
                self.balanceWindow.startGetBalanceThread()
        except Exception as ex:
            logger.error(ex)

    def openAutoTradeSetWindow(self) -> None:
        """Открытие окна настроек параметров и запуска автоматической торговли"""

        try:
            self.autoTradeSetWindow = AutoTradeSetWindow(self)
            self.autoTradeSetWindow.show()
            self.autoTradeSetWindow.exec_()
        except Exception as ex:
            logger.error(ex)

    def enableImitationMode(self) -> None:
        """Активация режима имитации торговли"""

        CryptoMonkeyGui.imitationMode = self.ui.checkBox_enableImitatitonTrade.isChecked()
        Settings.imitationMode = self.ui.checkBox_enableImitatitonTrade.isChecked()


    ### Методы запуска функций получения/передачи данных в отдельных потоках ###

    def startParsingThread(self) -> None:
        """Запуск потока парсинга для получения информации о котировках"""

        try:
            self.startParsButtonClicked = True
            self.parsThread_1 = ParsThread()
            self.computeThread_1 = QThread()
            self.parsThread_1.moveToThread(self.computeThread_1)
            self.computeThread_1.started.connect(self.parsThread_1.getCoinsInfo)
            self.parsThread_1.finishSignal.connect(self.computeThread_1.quit)
            self.parsThread_1.finishSignal.connect(self.renderParsResult)
            self.computeThread_1.start()
        except Exception as ex:
            logger.info(ex)

    def startPlaceOrderThread(self) -> None:
        """Запуск потока размещения ордера"""

        try:
            self.ui.pushButton_placeOrder.setDisabled(True)
            exchange = self.ui.comboBox_exchangeType.currentText().lower()
            dealType = self.ui.comboBox_dealType.currentText()
            orderType = self.ui.comboBox_orderType.currentText()

            if dealType == 'Покупка':
                dealType = 'buy'
            else:
                dealType = 'sell'
            if orderType == 'Лимитный':
                orderType = 'Limit'
            elif orderType == 'Рыночный':
                orderType = 'Market'

            order = dealType + orderType
            symbol = self.ui.comboBox_tradeQuotCoin.currentText().lower() + \
                     self.ui.comboBox_tradeBaseCoin.currentText().lower()
            amount = int(self.ui.spinBox_buyAmount.text())
            price = float(self.ui.doubleSpinBox_currencyPrice.text().replace(',','.'))
            imitationMode = self.ui.checkBox_enableImitatitonTrade.checkState()

            self.parsThread_2 = ParsThread(exchange, symbol, order, amount, price, imitationMode)
            self.computeThread_2 = QThread()
            self.parsThread_2.moveToThread(self.computeThread_2)
            self.computeThread_2.started.connect(self.parsThread_2.placeOrder)
            self.parsThread_2.finishSignal.connect(self.computeThread_2.quit)
            self.parsThread_2.finishSignal.connect(self.renderOrderData)
            self.computeThread_2.start()
        except Exception as ex:
            logger.info(ex)

    def startCancelingOrder(self) -> None:
        """Запуск потока отмены размещенного ордера"""

        try:
            self.ui.pushButton_cancelOrder.setDisabled(True)
            rowNum = self.ui.tableWidget_activeOrdersWindow.currentItem().row()
            if self.ui.tableWidget_activeOrdersWindow.item(rowNum, 5).text() == 'Canceled':
                return
            orderId = self.ui.tableWidget_activeOrdersWindow.item(rowNum, 0).text().replace('\n', '').split('/')[1]
            symbol = self.ui.tableWidget_activeOrdersWindow.item(rowNum, 1).text()
            exchange = self.ui.tableWidget_activeOrdersWindow.item(rowNum, 4).text()
            imitationMode = self.ui.checkBox_enableImitatitonTrade.checkState()
        except Exception:
            self.ui.tableWidget_diagWindow.item(CryptoMonkeyGui.unfilledDiagRowNum, 0).setText('Выберите строку с ордером для отмены!')
            logger.info('Выберите строку с ордером для отмены!')
            return
        try:
            self.parsThread_3 = ParsThread(exchange, orderId, symbol, imitationMode)
            self.computeThread_3 = QThread()
            self.parsThread_3.moveToThread(self.computeThread_3)
            self.computeThread_3.started.connect(self.parsThread_3.cancelOrder)
            self.parsThread_3.finishSignal.connect(self.computeThread_3.quit)
            self.parsThread_3.finishSignal.connect(self.renderCanceledOrderData)
            self.computeThread_3.start()
        except Exception as ex:
            logger.error(ex)

    def startOrdersInfoThread(self) -> None:
        """Запуск потока получения информации об открытых ордерах"""

        exchange = self.ui.comboBox_exchangeType.currentText().lower()
        symbol = self.ui.comboBox_tradeQuotCoin.currentText().lower() + self.ui.comboBox_tradeBaseCoin.currentText().lower()
        imitationMode = self.ui.checkBox_enableImitatitonTrade.checkState()

        try:
            self.parsThread_4 = ParsThread(exchange, symbol, imitationMode)
            self.computeThread_4 = QThread()
            self.parsThread_4.moveToThread(self.computeThread_4)
            self.computeThread_4.started.connect(self.parsThread_4.getOrdersInfo)
            self.parsThread_4.finishSignal.connect(self.computeThread_4.quit)
            self.parsThread_4.finishSignal.connect(self.renderOpenOrdersInfo)
            self.computeThread_4.start()
        except Exception as ex:
            logger.error(ex)


    ### Методы рендеринга полученных данных ###

    def renderParsResult(self, parsData: list) -> None:
        """Обработка полученных информационных данных о котировках выбранных валют на выбранных биржах"""

        try:
            cryptoMarkets = []
            cryptoMarketsData = []
            rowsCount = 0
            self.infoUnfilledRowNumber = 0

            self.ui.tableWidget_mainResultWindow.clearContents()
            self.ui.tableWidget_mainResultWindow.setRowCount(13)

            if self.ui.treeWidget_siteList.topLevelItem(0).checkState(0) == 2:
                cryptoMarkets.append('MYFIN')
                cryptoMarketsData.append(parsData[0])
            if self.ui.treeWidget_siteList.topLevelItem(1).checkState(0) == 2:
                cryptoMarkets.append('KUCOIN')
                cryptoMarketsData.append(parsData[1])
            if self.ui.treeWidget_siteList.topLevelItem(2).checkState(0) == 2:
                cryptoMarkets.append('COINBASE')
                cryptoMarketsData.append(parsData[2])

            if self.ui.checkBox_allCoinsRender.isChecked():
                for cryptoMarketData in cryptoMarketsData:
                    rowsCount += len(cryptoMarketData)
                self.ui.tableWidget_mainResultWindow.setRowCount(rowsCount)

            for cryptoMarket, cryptoMarketData in zip(cryptoMarkets, cryptoMarketsData):
                self.fillResultWindow(cryptoMarket, cryptoMarketData)
        except Exception as ex:
            logger.error(ex)

    def fillResultWindow(self, cryptoMarket: str, cryptoMarketData: list) -> None:
        """Отрисовка (заполнение) полученных информационных данных о котировках выбранных валют на выбранных биржах"""

        def addTableItem(text: str) -> object:
            item = QtWidgets.QTableWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignCenter)
            item.setText(text)
            return item
        item = addTableItem

        if not self.ui.checkBox_allCoinsRender.isChecked():  # рендеринг котировок одной выбранной криптомонеты
            self.ui.tableWidget_mainResultWindow.setItem(self.infoUnfilledRowNumber, 0, item(cryptoMarket))
            self.ui.tableWidget_mainResultWindow.setItem(self.infoUnfilledRowNumber, 1, item(
                f'{self.selectedQuotationCoin}/{self.selectedBasicCoin}'))
            for key in cryptoMarketData:
                if self.selectedQuotationCoin.lower() in key.lower():
                    self.ui.tableWidget_mainResultWindow.setItem(self.infoUnfilledRowNumber, 2, item(
                        str(cryptoMarketData.get(key))))
                    self.infoUnfilledRowNumber += 1
                    return
            self.ui.tableWidget_mainResultWindow.setItem(self.infoUnfilledRowNumber, 2, item('Котировка отсутствует'))
            self.infoUnfilledRowNumber += 1
        else:  # рендеринг котировок всех криптомонет
            for key in cryptoMarketData:
                self.ui.tableWidget_mainResultWindow.setItem(self.infoUnfilledRowNumber, 0, item(cryptoMarket))
                self.ui.tableWidget_mainResultWindow.setItem(self.infoUnfilledRowNumber, 1, item(
                    f'{key}/{self.selectedBasicCoin}'))
                self.ui.tableWidget_mainResultWindow.setItem(self.infoUnfilledRowNumber, 2, item(
                    str(cryptoMarketData.get(key))))
                self.infoUnfilledRowNumber += 1

    def renderOrderData(self, orderResultData: list) -> None:
        """Отрисовка данных о размещенном ордере"""

        self.ui.pushButton_placeOrder.setDisabled(False)
        orderResultData = orderResultData[0]

        def addTableItem(text):
            item = QtWidgets.QTableWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignCenter)
            item.setText(text)
            return item
        item = addTableItem

        if self.ordersUnfilledRowNumber >= 5:
            self.ui.tableWidget_activeOrdersWindow.setRowCount(self.ordersUnfilledRowNumber + 1)
            self.ui.tableWidget_activeOrdersWindow.verticalHeader().setStretchLastSection(False)
        else:
            self.ui.tableWidget_activeOrdersWindow.setRowCount(5)

        for i in range(self.ui.tableWidget_activeOrdersWindow.rowCount()):
            self.ui.tableWidget_activeOrdersWindow.verticalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)
        self.ui.tableWidget_activeOrdersWindow.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)

        self.ui.tableWidget_activeOrdersWindow.setItem(self.ordersUnfilledRowNumber, 0, item(f"{orderResultData['type']}/\n{orderResultData['id']}"))
        self.ui.tableWidget_activeOrdersWindow.setItem(self.ordersUnfilledRowNumber, 1, item(orderResultData['symbol']))
        self.ui.tableWidget_activeOrdersWindow.setItem(self.ordersUnfilledRowNumber, 2, item(str(orderResultData['amount'])))
        self.ui.tableWidget_activeOrdersWindow.setItem(self.ordersUnfilledRowNumber, 3, item(str(orderResultData['price'])))
        self.ui.tableWidget_activeOrdersWindow.setItem(self.ordersUnfilledRowNumber, 4, item(orderResultData['exchange']))
        item = item(orderResultData['state'])
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        brush = QtGui.QBrush(QtGui.QColor(14, 255, 22))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setBackground(brush)
        self.ui.tableWidget_activeOrdersWindow.setItem(self.ordersUnfilledRowNumber, 5, item)
        self.ordersUnfilledRowNumber += 1

    def renderCanceledOrderData(self, cancelResult: list) -> None:
        """Отрисовка данных об отмене ордера"""

        try:
            self.ui.pushButton_cancelOrder.setDisabled(False)

            def addTableItem(text):
                item = QtWidgets.QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignCenter)
                item.setText(text)
                return item
            item = addTableItem

            for row in range(self.ui.tableWidget_activeOrdersWindow.rowCount()):
                if self.ui.tableWidget_activeOrdersWindow.item(row, 0).text().replace('\n', '').split('/')[1] == cancelResult[1]:
                    item = item(cancelResult[2])
                    item.setFlags(QtCore.Qt.ItemIsEnabled)
                    brush = QtGui.QBrush(QtGui.QColor(255, 40, 25))
                    brush.setStyle(QtCore.Qt.SolidPattern)
                    item.setBackground(brush)
                    self.ui.tableWidget_activeOrdersWindow.setItem(row, 5, item)
                    break
        except Exception as ex:
            logger.info(ex)

    def renderOpenOrdersInfo(self, openOrdersData: list) -> None:
        """Отрисовка данных об открытых ордерах"""

        self.ordersUnfilledRowNumber = len(openOrdersData)
        self.ui.tableWidget_activeOrdersWindow.clearContents()

        def addTableItem(text):
            item = QtWidgets.QTableWidgetItem()
            item.setTextAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignCenter)
            item.setText(text)
            return item
        item = addTableItem

        if not openOrdersData:
            self.ui.tableWidget_diagWindow.setItem(0, 0, item('Открытые ордеры на выбранной бирже отсутсвуют!'))
            return

        if len(openOrdersData) >= (self.ui.tableWidget_activeOrdersWindow.rowCount()):
            self.ui.tableWidget_activeOrdersWindow.setRowCount(len(openOrdersData))
            self.ui.tableWidget_activeOrdersWindow.verticalHeader().setStretchLastSection(False)

        for i in range(self.ui.tableWidget_activeOrdersWindow.rowCount()):
            self.ui.tableWidget_activeOrdersWindow.verticalHeader().setSectionResizeMode(i,
                                                                                    QtWidgets.QHeaderView.ResizeToContents)
        self.ui.tableWidget_activeOrdersWindow.horizontalHeader().setSectionResizeMode(0,
                                                                                       QtWidgets.QHeaderView.ResizeToContents)
        for openOrder, i in zip(openOrdersData, range(len(openOrdersData))):
            try:
                self.ui.tableWidget_activeOrdersWindow.setItem(i, 0, item(f"{openOrder['type']}/\n{openOrder['id']}"))
                self.ui.tableWidget_activeOrdersWindow.setItem(i, 1, item(openOrder['symbol']))
                self.ui.tableWidget_activeOrdersWindow.setItem(i, 2, item(str(openOrder['amount'])))
                self.ui.tableWidget_activeOrdersWindow.setItem(i, 3, item(str(openOrder['price'])))
                self.ui.tableWidget_activeOrdersWindow.setItem(i, 4, item(openOrder['exchange']))
            except Exception as ex:
                logger.info(ex)
            item1 = item(openOrder['state'])
            item1.setFlags(QtCore.Qt.ItemIsEnabled)
            if openOrder['state'] == 'Active':
                brush = QtGui.QBrush(QtGui.QColor(14, 255, 22))
            elif openOrder['state'] == 'Canceled' or openOrder['state'] == 'Cancel error':
                brush = QtGui.QBrush(QtGui.QColor(255, 40, 25))
            else:
                brush = QtGui.QBrush(QtGui.QColor(255, 40, 25))
            brush.setStyle(QtCore.Qt.SolidPattern)
            item1.setBackground(brush)
            self.ui.tableWidget_activeOrdersWindow.setItem(i, 5, item1)

    def closeEvent(self, event) -> None:
        """Выпонение операций при закрытии основного окна приложения"""

        try:
            if CryptoMonkeyGui.balanceWinOpen:
                sys.exit(self.balanceWindow.exec_())
        except Exception:
            pass

class KeysInputWindow(Ui_Dialog_apiKeysInput, QDialog):
    """Класс-обертка для окна ввода ключей API личного кабинета пользователя"""

    userTokensData = {}

    def __init__(self, mainWindowUi):
        super(KeysInputWindow, self).__init__()
        self.keysInputWindow = Ui_Dialog_apiKeysInput()
        self.keysInputWindow.setupUi(self)
        self.mainWindowUi = mainWindowUi
        self.setKeysDataFromFile()
        self.add_functions()

    def setKeysDataFromFile(self):
        """Заполнение полей ввода ключей из файла"""

        try:
            exchange = self.keysInputWindow.comboBox_exchangeType.currentText().lower()
            userToken = []

            if os.path.exists(CryptoMonkeyGui.keysPath):
                with open(CryptoMonkeyGui.keysPath, "r") as file:
                    dataFromFile = file.readline().strip()
                    self.userTokensData = json.loads(dataFromFile)

            for exchangeKey in self.userTokensData:
                if exchangeKey == exchange:
                    userToken = self.userTokensData.get(exchange).split(',')

            if userToken:
                self.keysInputWindow.lineEdit_apiKeyInput.setText(userToken[0])
                self.keysInputWindow.lineEdit_secretKeyInput.setText(userToken[1])
        except Exception as ex:
            logger.error(ex)

    def add_functions(self):
        """Добавление функций обработки действий пользователя в GUI"""

        try:
            self.keysInputWindow.pushButton_keysInputEnable.clicked.connect(self.enableKeysInput)
            self.keysInputWindow.comboBox_exchangeType.currentIndexChanged.connect(self.setKeysDataFromFile)
        except Exception as ex:
            logger.error(ex)

    def enableKeysInput(self):
        """Сохранение введнных API-ключей в файл"""

        try:
            exchange = self.keysInputWindow.comboBox_exchangeType.currentText().lower()
            self.userTokensData[exchange] = f'{self.keysInputWindow.lineEdit_apiKeyInput.text()},' \
                                            f'{self.keysInputWindow.lineEdit_secretKeyInput.text()}'
            serializedTokensData = json.dumps(self.userTokensData)

            with open(CryptoMonkeyGui.keysPath, "w") as file:
                file.write(serializedTokensData)

            availableExchanges = []
            for token in self.userTokensData:
                if [char for char in self.userTokensData[token] if char.isdigit()] or \
                        [char for char in self.userTokensData[token] if char.isalpha()]:
                    availableExchanges.append(token.capitalize())
            self.mainWindowUi.enableTradeSettings(availableExchanges)

        except Exception as ex:
            logger.error(ex)

class BalanceWindow(Ui_BalanceWindow, QDialog):
    """Класс-обертка для окна отображения балансов личного кабинета пользователя"""

    refreshTime = 3

    def __init__(self, mainWindowUi):
        super(BalanceWindow, self).__init__()
        self.balanceWindow = Ui_BalanceWindow()
        self.balanceWindow.setupUi(self)
        self.mainWindowUi = mainWindowUi
        self.add_functions()
        self.startGetBalanceThread()


    ### Методы обработки действий пользователя ###

    def add_functions(self) -> None:
        """Добавление функций обработки действий пользователя в окне Балансы пользователя"""

        self.balanceWindow.pushButton_EnableBalanceRefreshTime.clicked.connect(self.setRefreshTime)
        self.balanceWindow.checkBox_circularRefreshBalance.clicked.connect(self.circularRefreshSwitcher)

    def setRefreshTime(self) -> None:
        """Установка времени обновления данных о боалансах пользователя"""

        BalanceWindow.refreshTime = self.balanceWindow.spinBox_balanceRefreshTime.value()

    def circularRefreshSwitcher(self) -> None:
        """Включение циклического получения и обновления данных о ненулевых балансах пользователя на выбранной бирже"""

        if self.balanceWindow.checkBox_circularRefreshBalance.isChecked():
            self.mainWindowUi.ui.pushButton_getBalances.setDisabled(True)

            self.balanceWindow.label_balanceRefreshTime.setDisabled(False)
            self.balanceWindow.spinBox_balanceRefreshTime.setDisabled(False)
            self.balanceWindow.pushButton_EnableBalanceRefreshTime.setDisabled(False)
            CryptoMonkeyGui.balanceAutoRefreshOn = True
            ParsThread.balanceAutoRefreshOn = True
            self.balanceRefreshTime = self.balanceWindow.spinBox_balanceRefreshTime.value()
            ParsThread.balanceRefreshTime = self.balanceWindow.spinBox_balanceRefreshTime.value()
            self.startGetBalanceThread()
        else:
            self.mainWindowUi.ui.pushButton_getBalances.setDisabled(False)
            self.balanceWindow.label_balanceRefreshTime.setDisabled(True)
            self.balanceWindow.spinBox_balanceRefreshTime.setDisabled(True)
            self.balanceWindow.pushButton_EnableBalanceRefreshTime.setDisabled(True)
            CryptoMonkeyGui.balanceAutoRefreshOn = False
            ParsThread.balanceAutoRefreshOn = False

            ### Методы запуска функций получения/передачи данных в отдельных потоках ###

    def startGetBalanceThread(self) -> None:
        """Запуск функции получения информации о ненулевых балансах пользователя на выбранной бирже"""

        try:
            exchange = self.mainWindowUi.ui.comboBox_exchangeType.currentText().lower()
            self.parsThread = ParsThread(exchange, self.mainWindowUi)
            self.computeThread = QThread()
            self.parsThread.moveToThread(self.computeThread)
            self.computeThread.started.connect(self.parsThread.getBalances)
            self.parsThread.finishSignal.connect(self.computeThread.quit)
            self.parsThread.finishSignal.connect(self.renderBalanceData)
            self.computeThread.start()
        except Exception as ex:
            logger.info(ex)


    ### Методы рендеринга полученных данных ###

    def renderBalanceData(self, balances: list) -> None:
        """Отрисовка данных о ненулевых балансах пользователя на выбранной бирже"""

        try:
            del balances[0]
            unfilledRowNumber = 0
            self.balanceWindow.tableWidget_balanceTable.clearContents()
            self.balanceWindow.tableWidget_balanceTable.setRowCount(10)

            def addTableItem(text):
                item = QtWidgets.QTableWidgetItem()
                item.setTextAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignCenter)
                item.setText(text)
                return item
            item = addTableItem

            for coinBalance in balances:
                if unfilledRowNumber >= (self.balanceWindow.tableWidget_balanceTable.rowCount() + 1):
                    self.balanceWindow.tableWidget_balanceTable.setRowCount(self.balanceWindow.tableWidget_balanceTable.rowCount() + 1)
                self.balanceWindow.tableWidget_balanceTable.setItem(unfilledRowNumber, 0, item(coinBalance.get('currency').upper()))
                self.balanceWindow.tableWidget_balanceTable.setItem(unfilledRowNumber, 1, item(coinBalance.get('balance')))
                unfilledRowNumber += 1
        except Exception as ex:
            logger.error(ex)


    def closeEvent(self, event) -> None:
        """Выпонение операций при закрытии окна Балансы пользователя"""

        try:
            CryptoMonkeyGui.balanceWinOpen = False
            CryptoMonkeyGui.balanceAutoRefreshOn = False
        except Exception as ex:
            logger.error(ex)

class AutoTradeSetWindow(Ui_TradeSettingsWindow, QDialog):
    """Класс-обертка для окна настройки параметров и запуска автоматической торговли"""

    def __init__(self, mainWindowUi):
        super(AutoTradeSetWindow, self).__init__()

        self.tradeSettingsWindow = Ui_TradeSettingsWindow()
        self.tradeSettingsWindow.setupUi(self)
        self.mainWindowUi = mainWindowUi
        self.addCoins()
        self.add_functions()

    def add_functions(self):
        self.tradeSettingsWindow.pushButton_startTrade.clicked.connect(self.getTradeSetttings)
        self.tradeSettingsWindow.pushButton_stopTrade.clicked.connect(self.stopTrade)
        self.tradeSettingsWindow.pushButton_EnableRefreshTime.clicked.connect(self.enableRefreshTime)

    def enableRefreshTime(self):
        Settings.priceRefreshTime = self.tradeSettingsWindow.spinBox_refreshTime.value()

    def getTradeSetttings(self):
        """Получение настроек и запуск торгового потока"""

        logger.info("Есть запуск торгового бота")
        TelegramBot.sendText("Есть запуск торгового бота")
        try:
            Settings.exchange = self.tradeSettingsWindow.comboBox_exchangeType.currentText().lower()
            Settings.quoteCurrency = self.tradeSettingsWindow.comboBox_tradeQuotCoin.currentText().lower()
            Settings.baseCurrency = self.tradeSettingsWindow.comboBox_tradeBaseCoin.currentText().lower()
            Settings.orderType = self.tradeSettingsWindow.comboBox_orderType.currentText()
            if Settings.imitationMode:
                Settings.startBalance = self.tradeSettingsWindow.spinBox_startBalance.value()
            if Settings.orderType == 'Лимитный':
                Settings.orderType = 'buyLimit'
            elif Settings.orderType == 'Рыночный':
                Settings.orderType = 'buyMarket'

            Settings.percentStartCondition = self.tradeSettingsWindow.doubleSpinBox_percentStartCondition.value()
            Settings.priceStartCondition = self.tradeSettingsWindow.doubleSpinBox_priceStartCondition.value()
            Settings.purchaseAmount = self.tradeSettingsWindow.doubleSpinBox_purchaseAmount.value()

            Settings.posBranch_upPercent = self.tradeSettingsWindow.doubleSpinBox_positiveBranch_upPercent.value()
            Settings.posBranch_sellPercent = self.tradeSettingsWindow.doubleSpinBox_positiveBranch_sellPercent.value()
            Settings.posBranch_upPercent2 = self.tradeSettingsWindow.doubleSpinBox_positiveBranch_upPercent_2.value()
            Settings.posBranch_upSellPercent2 = self.tradeSettingsWindow.doubleSpinBox_positiveBranch_upSellPercent_2.value()
            Settings.posBranch_downPercent3 = self.tradeSettingsWindow.doubleSpinBox_positiveBranch_downPercent_3.value()
            Settings.posBranch_downSellPercent3 = self.tradeSettingsWindow.doubleSpinBox_positiveBranch_downSellPercent_3.value()
            Settings.posBranch_upPercent4 = self.tradeSettingsWindow.doubleSpinBox_positiveBranch_upPercent_4.value()
            Settings.posBranch_upSellPercent4 = self.tradeSettingsWindow.doubleSpinBox_positiveBranch_upSellPercent_4.value()
            Settings.posBranch_downPercent4 = self.tradeSettingsWindow.doubleSpinBox_positiveBranch_downPercent_4.value()
            Settings.posBranch_downSellPercent4 = self.tradeSettingsWindow.doubleSpinBox_positiveBranch_downSellPercent_4.value()

            Settings.negBranch_downPercent1 = self.tradeSettingsWindow.doubleSpinBox_negativeBranch_downPercent_1.value()
            Settings.negBranch_averagePercent1 = self.tradeSettingsWindow.doubleSpinBox_negativeBranch_averagePercent_1.value()
            Settings.negBranch_downPercent2 = self.tradeSettingsWindow.doubleSpinBox_negativeBranch_downPercent_2.value()
            Settings.negBranch_averagePercent2 = self.tradeSettingsWindow.doubleSpinBox_negativeBranch_averagePercent_2.value()
            Settings.negBranch_upPercent1 = self.tradeSettingsWindow.doubleSpinBox_negativeBranch_upPercent1.value()
            Settings.negBranch_upSellPercent1 = self.tradeSettingsWindow.doubleSpinBox_negativeBranch_upSellPercent1.value()
            Settings.negBranch_long1 = self.tradeSettingsWindow.doubleSpinBox_negativeBranch_long1.value()
            Settings.negBranch_sellAllLong1 = self.tradeSettingsWindow.doubleSpinBox_negativeBranch_sellAllLong1.value()
            logger.info("Настройки алгоритма торговли введены")
            TelegramBot.sendText("Настройки алгоритма торговли введены")
        except Exception as ex:
            logger.error(ex)

        if os.path.exists(CryptoMonkeyGui.keysPath):
            with open(CryptoMonkeyGui.keysPath, "r") as file:
                dataFromFile = file.readline().strip()
            if Settings.exchange == 'huobi':
                Settings.keys = json.loads(dataFromFile).get('huobi').split(',')
        else:
            logger.info("Отсутствует файл с ключами пользователя")
            return

        self.startProcessThread()

    def startProcessThread(self) -> None:
        """Запуск алгоритма автоматической торговли в отдельнои потоке"""

        try:
            self.processThread = ProcessThread()
            self.computeThread_1 = QThread()
            self.processThread.moveToThread(self.computeThread_1)
            self.computeThread_1.started.connect(self.processThread.startWorking)
            self.processThread.finishSignal.connect(self.computeThread_1.quit)
            #self.processThread.finishSignal.connect(self.renderOpenOrdersInfo)
            self.computeThread_1.start()
        except Exception as ex:
            logger.error(ex)

    def stopTrade(self):
        Settings.loopStopCond = True

    def addCoins(self):
        """Синхронизация валют с перечнем валют в центральном окне приложения"""

        centralCoinModel = self.mainWindowUi.ui.comboBox_quotationCoin.model()
        self.tradeSettingsWindow.comboBox_tradeQuotCoin.clear()
        self.tradeSettingsWindow.comboBox_tradeQuotCoin.setModel(centralCoinModel)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = CryptoMonkeyGui()
    w.show()
    sys.exit(app.exec_())
