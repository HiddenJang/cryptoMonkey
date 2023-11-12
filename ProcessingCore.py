from PyQt5 import QtCore
from PyQt5.QtCore import QThread, QObject
from CryptoCoinBroker import CryptoBroker
from DataBase import DataBase
from TelegramBot import TelegramBot
from parserJson import startParsing
import asyncio
import os
import sys
import logging
import json
import sqlite3

## Принудительное переключение рабочей директории ##
file_path = os.path.realpath(__file__).rsplit('\\', 1)[0]
os.chdir(file_path)

logger = logging.getLogger('CryptoMonkey.ProcessingCore')


class ParsThread(QObject):
    """Класс получения данных с сайтов криптоплощадок и взаимодействия с базой данных в отдельном потоке
    !!!НЕ ИСПОЛЬЗУЕТСЯ ПРИ АВТОМАТИЧЕСКОЙ ТОРГОВЛЕ!!!"""

    finishSignal = QtCore.pyqtSignal(list)

    keysPath = 'D:\\Pasha\\python\\projects\\user_data.txt'  # путь к файлу с ключами от аккаунта пользователя
    baseCoin = 'USDT'
    circularRefreshOn = False
    refreshTime = 0
    balanceAutoRefreshOn = False
    balanceRefreshTime = 0

    def __init__(self, *args):
        super(ParsThread, self).__init__()
        self.args = args

    def getCoinsInfo(self) -> list:
        """Получение данных по выбранным валютам на выбранных биржах"""

        try:
            while True:
                parsData = asyncio.run(startParsing(self.baseCoin))
                self.finishSignal.emit(parsData)
                if not self.circularRefreshOn:
                    break
                QThread.sleep(self.refreshTime)
        except Exception as ex:
            logger.error(ex)

    def getBalances(self) -> list:
        """Получение данных о ненулевых балансах пользователя на выбранной бирже"""

        exchange = self.args[0]
        mainWindowUi = self.args[1]
        if os.path.exists(self.keysPath):
            with open(self.keysPath, "r") as file:
                dataFromFile = file.readline().strip()
            if exchange == 'huobi':
                keys = json.loads(dataFromFile).get('huobi').split(',')
        else:
            logger.info("Отсутствует файл с ключами пользователя")
            return
        while True:
            Broker = CryptoBroker(exchange, (keys[0], keys[1]))
            balances = Broker.getBalance()
            self.finishSignal.emit(balances)
            if not self.balanceAutoRefreshOn:
                mainWindowUi.ui.pushButton_getBalances.setDisabled(False)
                break
            QThread.sleep(self.refreshTime)

    def placeOrder(self) -> list:
        """Размещенние ордера на выбранной бирже"""

        orderResultData = {}
        exchange = self.args[0]
        symbol = self.args[1]
        orderType = self.args[2]
        amount = self.args[3]
        price = self.args[4]
        imitationMode = self.args[5]

        if os.path.exists(self.keysPath):
            with open(self.keysPath, "r") as file:
                dataFromFile = file.readline().strip()
            if exchange == 'huobi':
                keys = json.loads(dataFromFile).get('huobi').split(',')
        else:
            logger.info("Отсутствует файл с ключами пользователя")
            return

        Broker = CryptoBroker(exchange, (keys[0], keys[1]))
        orderData = Broker.startTrade(symbol, orderType, amount, price, imitationMode)
        if not orderData:
            return
        orderId = orderData[0]
        orderType = orderData[1]

        orderResultData['id'] = orderId
        orderResultData['exchange'] = exchange
        orderResultData['symbol'] = symbol
        orderResultData['type'] = orderType
        orderResultData['amount'] = amount
        orderResultData['price'] = price
        orderResultData['state'] = 'Active'

        dataBase = DataBase(sqlite3.connect('database.db'), imitationMode)
        dataBase.writeOrderInfo(orderResultData)
        self.finishSignal.emit([orderResultData])

    def cancelOrder(self) -> list:
        """Отмена размещенного ордера"""

        exchange = self.args[0]
        orderId = self.args[1]
        symbol = self.args[2]
        imitationMode = self.args[3]
        if os.path.exists(self.keysPath):
            with open(self.keysPath, "r") as file:
                dataFromFile = file.readline().strip()
            if exchange == 'huobi':
                keys = json.loads(dataFromFile).get('huobi').split(',')
        else:
            logger.info("Отсутствует файл с ключами пользователя")
            return
        Broker = CryptoBroker(exchange, (keys[0], keys[1]))
        result = Broker.cancelOrder(symbol, orderId, imitationMode)
        cancelResult = [exchange, orderId, result]

        dataBase = DataBase(sqlite3.connect('database.db'), imitationMode)
        dataBase.changeOrderInfo(cancelResult)
        self.finishSignal.emit(cancelResult)

    def getOrdersInfo(self) -> list:
        """Получение информации об открытых ордерах"""

        exchange = self.args[0]
        symbol = self.args[1]
        imitationMode = self.args[2]
        try:
            orders = []
            dataBase = DataBase(sqlite3.connect('database.db'), imitationMode)
            ordersList = dataBase.readOrderInfo()
            for order in ordersList:
                orders.append(json.loads(order[0]))
        except Exception as ex:
            logger.error(ex)
        self.finishSignal.emit(orders)


class Settings:
    """Класс настроек автоматической торговли"""

    exchange = 'huobi'
    quoteCurrency = 'xrp'
    baseCurrency = 'usdt'
    orderType = 'buyLimit'
    percentStartCondition = 5.00
    priceStartCondition = 0.00
    purchaseAmount = 10.00
    imitationMode = False
    posBranch_upPercent = 10.00
    posBranch_sellPercent = 50.00
    posBranch_upPercent2 = 10.00
    posBranch_upSellPercent2 = 25.00
    posBranch_downPercent3 = 5.00
    posBranch_downSellPercent3 = 25.00
    posBranch_upPercent4 = 10.00
    posBranch_upSellPercent4 = 25.00
    posBranch_downPercent4 = 5.00
    posBranch_downSellPercent4 = 25.00
    negBranch_downPercent1 = 5.00
    negBranch_averagePercent1 = 25.00
    negBranch_downPercent2 = 5.00
    negBranch_averagePercent2 = 25.00
    negBranch_upPercent1 = 10.00
    negBranch_upSellPercent1 = 50.00
    negBranch_long1 = 5.00
    negBranch_sellAllLong1 = 15.00

    startBalance = []
    startPrice = priceStartCondition
    currentPrice = 0.00
    keys = []
    algorithmState = 'sell'
    startAmount = 0
    currentAmount = 0
    lastOrderId = 0
    orderResultData = {}

    priceRefreshTime = 3
    loopStopCond = False
    cycleNum = 0

class ProcessThread(QObject):
    """Класс алгоритмов автоматической торговли"""

    keysPath = 'D:\\Pasha\\python\\projects\\user_data.txt'  # путь к файлу с ключами от аккаунта пользователя
    finishSignal = QtCore.pyqtSignal(list)

    def startWorking(self) -> None:
        logger.info("Есть запуск алгоритма торговли в отдельном потоке")
        TelegramBot.sendText("Есть запуск алгоритма торговли в отдельном потоке")
        logger.info(f'Settings.startBalance={Settings.startBalance}')
        Settings.loopStopCond = False

        dataBase = DataBase(sqlite3.connect('database.db'), Settings.imitationMode)
        dataBase.deleteAll()

        broker = CryptoBroker(Settings.exchange, (Settings.keys[0], Settings.keys[1]))
        while True:
            Settings.cycleNum += 1

            currencyData = broker.getCurrenciesPrice(Settings.quoteCurrency, Settings.baseCurrency)
            Settings.currentPrice = currencyData[0].get('price')
            logger.info("Текущая стоимость валюты получена")
            TelegramBot.sendText(f"Текущая стоимость валюты получена. "
                                 f"Биржа:{currencyData[0].get('exchange')}, "
                                 f"Пара:{currencyData[0].get('pare')},"
                                 f"Цена:{currencyData[0].get('price')}")

            Settings.startAmount = Settings.purchaseAmount // Settings.currentPrice
            Settings.currentAmount = Settings.startAmount
            symbol = Settings.quoteCurrency + Settings.baseCurrency

            if (Settings.currentPrice - Settings.currentPrice * Settings.percentStartCondition / 100) > Settings.priceStartCondition:
                Settings.startPrice = Settings.currentPrice - Settings.currentPrice * Settings.percentStartCondition / 100
                Settings.priceStartCondition = Settings.currentPrice - Settings.currentPrice * Settings.percentStartCondition / 100
            else:
                Settings.startPrice = Settings.priceStartCondition
                Settings.priceStartCondition = Settings.priceStartCondition

            if not Settings.imitationMode:
                startBalances = broker.getBalance()
            else:
                startBalances = [50550084, {'currency': Settings.baseCurrency, 'type': 'trade', 'balance': Settings.startBalance, 'available': Settings.startBalance}]

            del startBalances[0]
            for balance in startBalances:
                if balance.get('currency') == Settings.baseCurrency and balance.get('type') != 'frozen':
                    Settings.startBalance = float(balance.get('balance'))
                    logger.info(f"Текущий баланс получен. "
                                f"Валюта:{balance.get('currency')}, "
                                f"Баланс:{balance.get('balance')}")
                    TelegramBot.sendText(f"Текущий баланс получен. "
                                         f"Валюта:{balance.get('currency')}, "
                                         f"Баланс:{balance.get('balance')}")
            ## Размещаем ордер по стартовой цене ##
            orderData = broker.startTrade(symbol, Settings.orderType, Settings.startAmount, Settings.startPrice, Settings.imitationMode)
            if not orderData:
                return

            logger.info(f"Ордер размещен."
                                 f"Пара:{symbol}, "
                                 f"Тип:{Settings.orderType}, "
                                 f"Количество:{Settings.startAmount},"
                                 f"Цена:{Settings.startPrice},"
                                 f"Имитация:{Settings.imitationMode}")
            TelegramBot.sendText(f"Ордер размещен."
                                 f"Пара:{symbol}, "
                                 f"Тип:{Settings.orderType}, "
                                 f"Количество:{Settings.startAmount},"
                                 f"Цена:{Settings.startPrice},"
                                 f"Имитация:{Settings.imitationMode}")

            Settings.lastOrderId = orderData[0]

            currentBalances = broker.getBalance()
            del currentBalances[0]
            for balance in currentBalances:
                if balance.get('currency') == Settings.baseCurrency and balance.get('type') != 'frozen':
                    currentBalance = float(balance.get('balance'))
                    if Settings.imitationMode:
                        currentBalance = Settings.startBalance - Settings.startPrice * Settings.startAmount

            if (currentBalance < Settings.startBalance):
                Settings.orderResultData = {}
                orderId = orderData[0]
                orderType = orderData[1]

                Settings.orderResultData['id'] = orderId
                Settings.orderResultData['exchange'] = Settings.exchange
                Settings.orderResultData['symbol'] = symbol
                Settings.orderResultData['type'] = orderType
                Settings.orderResultData['amount'] = Settings.startAmount
                Settings.orderResultData['price'] = Settings.startPrice
                Settings.orderResultData['state'] = 'Active'
                try:
                    if Settings.imitationMode:
                        Settings.startBalance -= Settings.startPrice * Settings.startAmount
                        logger.info(f'Settings.startBalance={Settings.startBalance}')
                    dataBase.writeOrderInfo(Settings.orderResultData)
                    observer = Observer()
                    observer.startObserve()
                except Exception as ex:
                    logger.error(ex)

            else:
                logger.info("Нет изменения баланса после размещения ордера")


class Observer:
    """Класс мониторинга цены"""

    def startObserve(self) -> None:
        """Наблюдение за изменением стоимости выбранной валюты"""

        logger.info(f"Есть запуск мониторинга текущей цены. Номер запуска алгоритма: {Settings.cycleNum}")
        TelegramBot.sendText(f"Есть запуск мониторинга текущей цены. Номер запуска алгоритма: {Settings.cycleNum}")
        broker = CryptoBroker(Settings.exchange, (Settings.keys[0], Settings.keys[1]))
        dataBase = DataBase(sqlite3.connect('database.db'), Settings.imitationMode)
        n = 0
        filled = False
        while True:
            try:
                currencyData = broker.getCurrenciesPrice(Settings.quoteCurrency, Settings.baseCurrency)
                Settings.currentPrice = currencyData[0].get('price')
                if not filled:
                    orderState = broker.getOrderState(Settings.lastOrderId, Settings.imitationMode)  ## submitted - размещен, canceled - отменен, filled - исполнен
                    if orderState.get('state') == 'filled':
                        dataBase.changeOrderInfo([Settings.exchange, Settings.lastOrderId, 'filled'])
                ## Если текущая цена выросла более чем на 10% запускаем продажу заданного процента валюты ##

                ## код для имитации исполнения ордера ##
                ##############################
                if not filled and (Settings.orderType == "buyLimit" and Settings.currentPrice <= Settings.startPrice or Settings.orderType == 'buyMarket') and Settings.imitationMode:
                    orderState = {'state': 'filled'}
                    Settings.orderResultData['state'] = 'filled'
                    dataBase.changeOrderInfo([Settings.exchange, Settings.lastOrderId, 'filled'])
                    TelegramBot.sendText(
                        f"Ордер исполнен по цене {Settings.startPrice}. Идет мониторинг цены для перехода к одной из веток стратегии")
                    filled = True
                elif not filled and (Settings.orderType == "sellLimit" and Settings.currentPrice >= Settings.startPrice or Settings.orderType == 'sellMarket') and Settings.imitationMode:
                    orderState = {'state': 'filled'}
                    Settings.orderResultData['state'] = 'filled'
                    dataBase.changeOrderInfo([Settings.exchange, Settings.lastOrderId, 'filled'])
                    TelegramBot.sendText(
                        f"Ордер исполнен по цене {Settings.startPrice}. Идет мониторинг цены для перехода к одной из веток стратегии")
                    filled = True
                ##############################

                print(
                    f'orderState = {orderState}, '
                    f'Settings.currentPrice={Settings.currentPrice}, '
                    f'Settings.startPrice={Settings.startPrice}, '
                    f'Settings.posBranch_upPercent={Settings.posBranch_upPercent}'
                )

                if (orderState.get('state') == 'filled') and (Settings.currentPrice >= (
                        Settings.startPrice + Settings.startPrice * Settings.posBranch_upPercent / 100)):
                    positiveBranch = PositiveBranch()
                    print(f'startPriceP = {Settings.startPrice}')
                    TelegramBot.sendText(f"Зафиксирован рост цены на более чем {Settings.posBranch_upPercent} процентов. Переход к положительной ветке")
                    positiveBranch.blok1()
                    break

                elif (orderState.get('state') == 'filled') and (Settings.currentPrice <= (
                        Settings.startPrice - Settings.startPrice * Settings.negBranch_downPercent1 / 100)):
                    negativeBranch = NegativeBranch()
                    TelegramBot.sendText(
                        f"Зафиксировано падение цены более чем на {Settings.negBranch_downPercent1} процентов. Переход к отрицательной ветке")
                    print(f'startPriceN = {Settings.startPrice}')
                    negativeBranch.blok4()
                    break

                elif Settings.loopStopCond:
                    Settings.loopStopCond = False
                    logger.info("Завершение торговли по требованию пользователя")
                    TelegramBot.sendText("Завершение торговли по требованию пользователя")
                    return

                else:
                    QThread.sleep(Settings.priceRefreshTime)
                    print(f'Итерация:{n}')
                    n+=1
                    continue
            except Exception as ex:
                logger.info(ex)
                TelegramBot.sendText(ex)
        logger.info(f"Алгоритм торговли завершен. Текущий баланс: {Settings.startBalance}")
        TelegramBot.sendText(f"Алгоритм торговли завершен. Текущий баланс: {Settings.startBalance}")

class PositiveBranch:

    @staticmethod
    def blok1():
        logger.info('Есть запуск блока 1')
        TelegramBot.sendText('Есть запуск блока 1')
        broker = CryptoBroker(Settings.exchange, (Settings.keys[0], Settings.keys[1]))
        dataBase = DataBase(sqlite3.connect('database.db'), Settings.imitationMode)

        symbol = Settings.quoteCurrency + Settings.baseCurrency
        orderType = 'sellMarket'

        operationAmount = (Settings.startAmount * Settings.posBranch_sellPercent) // 100
        if operationAmount > Settings.currentAmount:
            operationAmount = Settings.currentAmount

        orderData = broker.startTrade(symbol, orderType, operationAmount, Settings.currentPrice, Settings.imitationMode)

        if Settings.imitationMode:
            Settings.startBalance += Settings.currentPrice * operationAmount
            logger.info(f'Settings.startBalance={Settings.startBalance}')

        Settings.orderResultData = {}
        orderId = orderData[0]
        orderType = orderData[1]

        Settings.orderResultData['id'] = orderId
        Settings.orderResultData['exchange'] = Settings.exchange
        Settings.orderResultData['symbol'] = symbol
        Settings.orderResultData['type'] = orderType
        Settings.orderResultData['amount'] = operationAmount
        Settings.orderResultData['price'] = Settings.currentPrice
        if Settings.imitationMode:
            Settings.orderResultData['state'] = 'filled'
        else:
            state = broker.getOrderState(orderId, Settings.imitationMode).get('state')
            Settings.orderResultData['state'] = state
        dataBase.writeOrderInfo(Settings.orderResultData)

        Settings.currentAmount -= operationAmount
        Settings.startPrice = Settings.currentPrice
        logger.info(f'Есть продажа {operationAmount} единиц валюты ({Settings.posBranch_sellPercent}%) по цене {Settings.currentPrice}. Текущее количество валюты:{Settings.currentAmount}. Есть завершение блока 1')
        TelegramBot.sendText(f'Есть продажа {operationAmount} единиц валюты ({Settings.posBranch_sellPercent}%) по цене {Settings.currentPrice}. Текущее количество валюты:{Settings.currentAmount}. Есть завершение блока 1')
        PositiveBranch.blok2()

    @staticmethod
    def blok2():
        logger.info('Есть запуск блока 2')
        TelegramBot.sendText('Есть запуск блока 2')
        broker = CryptoBroker(Settings.exchange, (Settings.keys[0], Settings.keys[1]))
        dataBase = DataBase(sqlite3.connect('database.db'), Settings.imitationMode)
        symbol = Settings.quoteCurrency + Settings.baseCurrency
        orderType = 'sellMarket'

        logger.info("Есть запуск мониторинга текущей цены в блоке 2")
        TelegramBot.sendText("Есть запуск мониторинга текущей цены в блоке 2")
        while True:
            currencyData = broker.getCurrenciesPrice(Settings.quoteCurrency, Settings.baseCurrency)
            Settings.currentPrice = currencyData[0].get('price')

            if Settings.currentPrice >= (Settings.startPrice + Settings.startPrice * Settings.posBranch_upPercent2 / 100):
                operationAmount = (Settings.startAmount * Settings.posBranch_upSellPercent2) // 100
                break

            elif Settings.currentPrice <= (Settings.startPrice - Settings.startPrice * Settings.posBranch_downPercent3 / 100):
                operationAmount = (Settings.startAmount * Settings.posBranch_downSellPercent3) // 100
                break

            elif Settings.loopStopCond:
                Settings.loopStopCond = False
                logger.info("Завершение торговли по требованию пользователя")
                TelegramBot.sendText("Завершение торговли по требованию пользователя")
                return

            else:
                QThread.sleep(Settings.priceRefreshTime)
                continue

        if operationAmount > Settings.currentAmount:
            operationAmount = Settings.currentAmount

        orderData = broker.startTrade(symbol, orderType, operationAmount, Settings.currentPrice, Settings.imitationMode)

        if Settings.imitationMode:
            Settings.startBalance += Settings.currentPrice * operationAmount
            logger.info(f'Settings.startBalance={Settings.startBalance}')

        Settings.orderResultData = {}
        orderId = orderData[0]
        orderType = orderData[1]

        Settings.orderResultData['id'] = orderId
        Settings.orderResultData['exchange'] = Settings.exchange
        Settings.orderResultData['symbol'] = symbol
        Settings.orderResultData['type'] = orderType
        Settings.orderResultData['amount'] = operationAmount
        Settings.orderResultData['price'] = Settings.currentPrice
        if Settings.imitationMode:
            Settings.orderResultData['state'] = 'filled'
        else:
            state = broker.getOrderState(orderId, Settings.imitationMode).get('state')
            Settings.orderResultData['state'] = state
        dataBase.writeOrderInfo(Settings.orderResultData)

        Settings.currentAmount -= operationAmount
        Settings.startPrice = Settings.currentPrice
        logger.info(f'Есть продажа {operationAmount} единиц валюты по цене {Settings.currentPrice}. Текущее количество валюты:{Settings.currentAmount}. Есть завершение блока 2')
        TelegramBot.sendText(f'Есть продажа {operationAmount} единиц валюты по цене {Settings.currentPrice}. Текущее количество валюты:{Settings.currentAmount}. Есть завершение блока 2')
        PositiveBranch.blok3()

    @staticmethod
    def blok3():
        logger.info('Есть запуск блока 3')
        TelegramBot.sendText('Есть запуск блока 3')
        broker = CryptoBroker(Settings.exchange, (Settings.keys[0], Settings.keys[1]))
        dataBase = DataBase(sqlite3.connect('database.db'), Settings.imitationMode)
        symbol = Settings.quoteCurrency + Settings.baseCurrency
        orderType = 'sellMarket'

        logger.info("Есть запуск мониторинга текущей цены в блоке 3")
        TelegramBot.sendText("Есть запуск мониторинга текущей цены в блоке 3")
        while True:
            currencyData = broker.getCurrenciesPrice(Settings.quoteCurrency, Settings.baseCurrency)
            Settings.currentPrice = currencyData[0].get('price')

            if Settings.currentPrice >= (
                    Settings.startPrice + Settings.startPrice * Settings.posBranch_upPercent4 / 100):
                operationAmount = (Settings.startAmount * Settings.posBranch_upSellPercent4) // 100
                break

            elif Settings.currentPrice <= (
                    Settings.startPrice - Settings.startPrice * Settings.posBranch_downPercent4 / 100):
                operationAmount = (Settings.startAmount * Settings.posBranch_downSellPercent4) // 100
                break

            elif Settings.loopStopCond:
                Settings.loopStopCond = False
                logger.info("Завершение торговли по требованию пользователя")
                TelegramBot.sendText("Завершение торговли по требованию пользователя")
                return

            else:
                QThread.sleep(Settings.priceRefreshTime)
                continue

        ## Для продажи всей оставшейся валюты ##
        if operationAmount != Settings.currentAmount:
            operationAmount = Settings.currentAmount

        orderData = broker.startTrade(symbol, orderType, operationAmount, Settings.currentPrice, Settings.imitationMode)

        if Settings.imitationMode:
            Settings.startBalance += Settings.currentPrice * operationAmount
            logger.info(f'Settings.startBalance={Settings.startBalance}')

        Settings.orderResultData = {}
        orderId = orderData[0]
        orderType = orderData[1]

        Settings.orderResultData['id'] = orderId
        Settings.orderResultData['exchange'] = Settings.exchange
        Settings.orderResultData['symbol'] = symbol
        Settings.orderResultData['type'] = orderType
        Settings.orderResultData['amount'] = operationAmount
        Settings.orderResultData['price'] = Settings.currentPrice
        if Settings.imitationMode:
            Settings.orderResultData['state'] = 'filled'
        else:
            state = broker.getOrderState(orderId, Settings.imitationMode).get('state')
            Settings.orderResultData['state'] = state
        dataBase.writeOrderInfo(Settings.orderResultData)

        Settings.currentAmount -= operationAmount
        Settings.startPrice = Settings.currentPrice
        logger.info(f'Есть продажа {operationAmount} единиц валюты по цене {Settings.currentPrice}. Текущее количество валюты:{Settings.currentAmount}. Есть завершение блока 3')
        TelegramBot.sendText(f'Есть продажа {operationAmount} единиц валюты по цене {Settings.currentPrice}. Текущее количество валюты:{Settings.currentAmount}. Есть завершение блока 3')

class NegativeBranch:

    @staticmethod
    def blok4():
        logger.info('Есть запуск блока 4')
        TelegramBot.sendText('Есть запуск блока 4')
        broker = CryptoBroker(Settings.exchange, (Settings.keys[0], Settings.keys[1]))
        dataBase = DataBase(sqlite3.connect('database.db'), Settings.imitationMode)
        symbol = Settings.quoteCurrency + Settings.baseCurrency
        orderType = 'buyMarket'

        operationPurchase = (Settings.purchaseAmount * Settings.negBranch_averagePercent1) // 100
        operationAmount = operationPurchase // Settings.currentPrice
        if operationAmount > Settings.currentAmount:
            operationAmount = Settings.currentAmount

        orderData = broker.startTrade(symbol, orderType, operationAmount, Settings.currentPrice, Settings.imitationMode)

        if Settings.imitationMode:
            Settings.startBalance -= Settings.currentPrice * operationAmount
            logger.info(f'Settings.startBalance={Settings.startBalance}')

        Settings.orderResultData = {}
        orderId = orderData[0]
        orderType = orderData[1]

        Settings.orderResultData['id'] = orderId
        Settings.orderResultData['exchange'] = Settings.exchange
        Settings.orderResultData['symbol'] = symbol
        Settings.orderResultData['type'] = orderType
        Settings.orderResultData['amount'] = operationAmount
        Settings.orderResultData['price'] = Settings.currentPrice
        if Settings.imitationMode:
            Settings.orderResultData['state'] = 'filled'
        else:
            state = broker.getOrderState(orderId, Settings.imitationMode).get('state')
            Settings.orderResultData['state'] = state
        dataBase.writeOrderInfo(Settings.orderResultData)

        Settings.currentAmount += operationAmount
        Settings.startPrice = Settings.currentPrice
        logger.info(f'Есть покупка {operationAmount} единиц валюты (усреднение 1 на {Settings.negBranch_averagePercent1}%) по цене {Settings.currentPrice}. Текущее количество валюты:{Settings.currentAmount}. Есть завершение блока 4')
        TelegramBot.sendText(f'Есть покупка {operationAmount} единиц валюты (усреднение 1 на {Settings.negBranch_averagePercent1}%) по цене {Settings.currentPrice}. Текущее количество валюты:{Settings.currentAmount}. Есть завершение блока 4')
        NegativeBranch.blok5()

    @staticmethod
    def blok5():
        logger.info('Есть запуск блока 5')
        TelegramBot.sendText('Есть запуск блока 5')
        broker = CryptoBroker(Settings.exchange, (Settings.keys[0], Settings.keys[1]))
        dataBase = DataBase(sqlite3.connect('database.db'), Settings.imitationMode)
        symbol = Settings.quoteCurrency + Settings.baseCurrency

        logger.info("Есть запуск мониторинга текущей цены в блоке 5")
        TelegramBot.sendText("Есть запуск мониторинга текущей цены в блоке 5")
        while True:
            currencyData = broker.getCurrenciesPrice(Settings.quoteCurrency, Settings.baseCurrency)
            Settings.currentPrice = currencyData[0].get('price')

            if Settings.currentPrice <= (
                    Settings.startPrice - Settings.startPrice * Settings.negBranch_downPercent2 / 100):
                orderType = 'buyMarket'
                operationPurchase = (Settings.purchaseAmount * Settings.negBranch_averagePercent2) // 100
                operationAmount = operationPurchase // Settings.currentPrice
                break

            elif Settings.currentPrice >= (
                    Settings.startPrice + Settings.startPrice * Settings.negBranch_upPercent1 / 100):
                orderType = 'sellMarket'
                operationAmount = (Settings.currentAmount * Settings.negBranch_upSellPercent1) // 100
                ## Для продажи всей оставшейся валюты ##
                operationAmount = Settings.currentAmount
                break

            elif Settings.loopStopCond:
                Settings.loopStopCond = False
                logger.info("Завершение торговли по требованию пользователя")
                TelegramBot.sendText("Завершение торговли по требованию пользователя")
                return

            else:
                QThread.sleep(Settings.priceRefreshTime)
                continue

        if operationAmount > Settings.currentAmount:
            operationAmount = Settings.currentAmount

        orderData = broker.startTrade(symbol, orderType, operationAmount, Settings.currentPrice, Settings.imitationMode)

        Settings.orderResultData = {}
        orderId = orderData[0]
        orderTypeDB = orderData[1]

        Settings.orderResultData['id'] = orderId
        Settings.orderResultData['exchange'] = Settings.exchange
        Settings.orderResultData['symbol'] = symbol
        Settings.orderResultData['type'] = orderTypeDB
        Settings.orderResultData['amount'] = operationAmount
        Settings.orderResultData['price'] = Settings.currentPrice
        if Settings.imitationMode:
            Settings.orderResultData['state'] = 'filled'
        else:
            state = broker.getOrderState(orderId, Settings.imitationMode).get('state')
            Settings.orderResultData['state'] = state
        dataBase.writeOrderInfo(Settings.orderResultData)

        if orderType == 'buyMarket':
            if Settings.imitationMode:
                Settings.startBalance -= Settings.currentPrice * operationAmount
                logger.info(f'Settings.startBalance={Settings.startBalance}')
            Settings.currentAmount += operationAmount

            logger.info(f'Есть покупка {operationAmount} единиц валюты (усреднение 2 на {Settings.negBranch_averagePercent2}%) по цене {Settings.currentPrice}. Текущее количество валюты:{Settings.currentAmount}. Есть завершение блока 5')
            TelegramBot.sendText(f'Есть покупка {operationAmount} единиц валюты (усреднение 2 на {Settings.negBranch_averagePercent2}%) по цене {Settings.currentPrice}. Текущее количество валюты:{Settings.currentAmount}. Есть завершение блока 5')
            NegativeBranch.blok6()
        else:
            if Settings.imitationMode:
                Settings.startBalance += Settings.currentPrice * operationAmount
                logger.info(f'Settings.startBalance={Settings.startBalance}')
            Settings.currentAmount -= operationAmount

            logger.info(
                f'Есть продажа {operationAmount} единиц валюты ({Settings.negBranch_upSellPercent1}%) по цене {Settings.currentPrice}. Текущее количество валюты:{Settings.currentAmount}. Есть завершение блока 5')
            TelegramBot.sendText(
                f'Есть продажа {operationAmount} единиц валюты ({Settings.negBranch_upSellPercent1}%) по цене {Settings.currentPrice}. Текущее количество валюты:{Settings.currentAmount}. Есть завершение блока 5')

        Settings.startPrice = Settings.currentPrice


    @staticmethod
    def blok6():
        logger.info('Есть запуск блока 6')
        TelegramBot.sendText('Есть запуск блока 6')
        broker = CryptoBroker(Settings.exchange, (Settings.keys[0], Settings.keys[1]))
        dataBase = DataBase(sqlite3.connect('database.db'), Settings.imitationMode)
        symbol = Settings.quoteCurrency + Settings.baseCurrency
        orderType = 'sellMarket'

        logger.info("Есть запуск мониторинга текущей цены в блоке 6")
        TelegramBot.sendText("Есть запуск мониторинга текущей цены в блоке 6")
        while True:
            currencyData = broker.getCurrenciesPrice(Settings.quoteCurrency, Settings.baseCurrency)
            Settings.currentPrice = currencyData[0].get('price')

            if Settings.currentPrice <= (Settings.startPrice + Settings.startPrice * Settings.negBranch_long1 / 100):
                logger.info(f'Есть падение цены валюты до {Settings.currentPrice}.')
                TelegramBot.sendText(f'Есть падение цены валюты до {Settings.currentPrice}.')
                operationAmount = Settings.currentAmount
                break

            elif Settings.currentPrice >= (Settings.startPrice + Settings.startPrice * Settings.negBranch_sellAllLong1 / 100):
                logger.info(f'Есть увеличение цены валюты до {Settings.currentPrice}.')
                TelegramBot.sendText(f'Есть увеличение цены валюты до {Settings.currentPrice}.')
                operationAmount = Settings.currentAmount
                break

            elif Settings.loopStopCond:
                Settings.loopStopCond = False
                logger.info("Завершение торговли по требованию пользователя")
                TelegramBot.sendText("Завершение торговли по требованию пользователя")
                return

            else:
                QThread.sleep(Settings.priceRefreshTime)
                continue

        orderData = broker.startTrade(symbol, orderType, operationAmount, Settings.currentPrice, Settings.imitationMode)

        if Settings.imitationMode:
            Settings.startBalance += Settings.currentPrice * operationAmount
            logger.info(f'Settings.startBalance={Settings.startBalance}')

        Settings.orderResultData = {}
        orderId = orderData[0]
        orderType = orderData[1]

        Settings.orderResultData['id'] = orderId
        Settings.orderResultData['exchange'] = Settings.exchange
        Settings.orderResultData['symbol'] = symbol
        Settings.orderResultData['type'] = orderType
        Settings.orderResultData['amount'] = operationAmount
        Settings.orderResultData['price'] = Settings.currentPrice
        if Settings.imitationMode:
            Settings.orderResultData['state'] = 'filled'
        else:
            state = broker.getOrderState(orderId, Settings.imitationMode).get('state')
            Settings.orderResultData['state'] = state
        dataBase.writeOrderInfo(Settings.orderResultData)

        Settings.currentAmount -= operationAmount
        Settings.startPrice = Settings.currentPrice
        logger.info(f'Есть продажа всей валюты ({operationAmount} единиц) по цене {Settings.currentPrice}. Текущее количество валюты:{Settings.currentAmount}. Есть завершение блока 6')
        TelegramBot.sendText(f'Есть продажа всей валюты ({operationAmount} единиц) по цене {Settings.currentPrice}. Текущее количество валюты:{Settings.currentAmount}. Есть завершение блока 6')