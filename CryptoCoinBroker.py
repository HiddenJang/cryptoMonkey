import logging
import requests
from huobi.client.account import AccountClient
from huobi.constant import *
from huobi.client.trade import TradeClient
from huobi.utils import *
from TelegramBot import TelegramBot
from time import sleep
import random


logger = logging.getLogger('CryptoMonkey.CryptoCoinBroker')

class CryptoBroker():
    """Класс взаимодействия с критобиржей"""

    def __init__(
            self,
            exchange: str,
            userToken: tuple
    ):
        self.exchange = exchange
        self.userToken = userToken

    def getAccountId(self) -> int:  # None если не удалось получить id аккаунта
        """Метод получения id спотового аккаунта пользователя"""

        if self.exchange == 'huobi':
            account_client = AccountClient(api_key=self.userToken[0], secret_key=self.userToken[1])
            accountId = None
            try:
                ### Получаем id спотового аккаунта пользователя ###
                accountList = account_client.get_accounts().get('data')
                for account in accountList:
                    if account.get('type') == 'spot':
                        accountId = account.get('id')
                        break
                if not accountId:
                    logger.error("Не удалось получить id спотового аккаунта пользователя")
                    TelegramBot.sendText("Не удалось получить id спотового аккаунта пользователя")
                    return []
            except Exception as ex:
                logger.error(ex)
                TelegramBot.sendText(str(ex))
        return accountId

    def getCurrenciesPrice(
            self,
            quoteCurrency: str,
            baseCurrency: str
    ) -> list:
        """Метод получения данных от выбранной криптобиржи по выбранным валютам"""

        currencyData = {}
        if self.exchange == 'huobi':
            url = f'https://api.huobi.pro/market/trade?symbol={quoteCurrency}{baseCurrency}'  ##текущая цена криптовалюты
            try:
                response = requests.get(url)
                currencyCommonData = response.json()
                currencyData["exchange"] = f'{self.exchange}'
                currencyData["pare"] = f'{quoteCurrency}/{baseCurrency}'
                currencyData["price"] = currencyCommonData["tick"]["data"][0]["price"]
                return [currencyData]
            except Exception as ex:
                logger.error(ex)
                TelegramBot.sendText(str(ex))
                return []

    def getBalance(self) -> list:
        """Метод получения ненулевых балансов пользователя"""

        if self.exchange == 'huobi':
            accountId = self.getAccountId()
            account_client = AccountClient(api_key=self.userToken[0], secret_key=self.userToken[1])
            try:
                ### Получаем все ненулевые балансы в аккаунте пользователя ###
                allCoinsBalance = account_client.get_balance(accountId).get('data').get('list')
                userBalances = [accountId]
                for coinBalance in allCoinsBalance:
                    if float(coinBalance.get("balance")) > 0:
                        userBalances.append({
                            'currency': coinBalance['currency'],
                            'type': coinBalance['type'],
                            'balance': coinBalance['balance'],
                            'available': coinBalance.get('available')
                        })
                return userBalances
            except Exception as ex:
                logger.error(ex)
                TelegramBot.sendText(str(ex))
                return []

    def startTrade(
            self,
            symbol: str,
            orderType: str,
            amount: float,
            price: float,  # None если выставляется ордер по рыночной цене (buyMarket или sellMarket)
            imitationMode: bool
    ) -> list:
        """Метод размещения ордера на покупку/продажу"""

        if self.exchange == 'huobi':
            accountId = self.getAccountId()
            ## Выставление ордера по лимитной цене покупаемой валюты ##
            if orderType == 'buyLimit':
                type = 'Buy_limit'
                orderType = OrderType.BUY_LIMIT
            elif orderType == 'sellLimit':
                type = 'Sell_limit'
                orderType = OrderType.SELL_LIMIT

            ## Выставление ордера по рыночной цене покупаемой валюты ##
            elif orderType == 'buyMarket':
                type = 'Buy_market'
                orderType = OrderType.BUY_MARKET
            elif orderType == 'sellMarket':
                type = 'Sell_market'
                orderType = OrderType.SELL_MARKET
            try:
                tradeClient = TradeClient(api_key=self.userToken[0], secret_key=self.userToken[1])
                if not imitationMode:
                    orderId = tradeClient.create_order(symbol=symbol, account_id=accountId, order_type=orderType,
                                                         source=OrderSource.API, amount=amount, price=price)
                    logger.info(f"Размещен ордер id : {orderId}, {type}, пара: {symbol} проведено успешно!")
                    TelegramBot.sendText(f"Размещен ордер id : {orderId}, {type}, пара: {symbol} проведено успешно!")
                else:
                    try:
                        orderId = tradeClient.create_order(symbol=symbol, account_id=accountId, order_type=orderType,
                                                           source=OrderSource.API, amount=startAmount, price=0.0)
                        logger.info(
                            f"Размещение ордера (имитация)  id : {orderId}, {type}, пара: {symbol} проведено успешно!")
                    except:
                        orderId = random.randint(000000000000000, 999999999999999)
                        logger.info(f"Размещение ордера (имитация)  id : {orderId}, {type}, пара: {symbol} проведено успешно!")

                return [orderId, type]
            except Exception as ex:
                logger.error(ex)
                TelegramBot.sendText(str(ex))
                return []

    def getOpenOrders(self, symbol: str) -> list:
        """Получение данных об открытых ордерах на выбранной бирже"""

        try:
            if self.exchange == 'huobi':
                accountId = self.getAccountId()
                tradeClient = TradeClient(api_key=self.userToken[0], secret_key=self.userToken[1])
                openOrderInfo = tradeClient.get_open_orders(symbol, accountId)
                return openOrderInfo
            else:
                return []
        except Exception as ex:
            logger.error(ex)

    def getOrderState(self, orderId: int, imitationMode: bool) -> dict:
        """Получение данных об ордере по ID"""

        try:
            if self.exchange == 'huobi':
                if not imitationMode:
                    tradeClient = TradeClient(api_key=self.userToken[0], secret_key=self.userToken[1])
                    OrderInfo = tradeClient.get_order(orderId)
                    return OrderInfo.get('data')
                else:
                    return {'state': 'submitted'}
            else:
                return []
        except Exception as ex:
            logger.error(ex)

    def cancelOrder(
            self,
            symbol: str,
            orderId: str,
            imitationMode: bool
    ) -> str:
        """Метод отмены выставленного ордера"""

        try:
            if imitationMode:
                canceledOrderId = orderId
                logger.info(f"Отмены ордера (имитация) id : {canceledOrderId}, пара: {symbol} проведена успешно!")
                TelegramBot.sendText(f"Отмены ордера (имитация) id : {canceledOrderId}, пара: {symbol} проведена успешно!")
                return 'Canceled'
            tradeClient = TradeClient(api_key=self.userToken[0], secret_key=self.userToken[1])
            canceledOrderId = tradeClient.cancel_order(symbol, orderId)
            if str(canceledOrderId) == str(orderId):
                logger.info(f"Отмена ордера id : {canceledOrderId}, пара: {symbol} проведена успешно!")
                TelegramBot.sendText(f"Отмена ордера id : {canceledOrderId}, пара: {symbol} проведена успешно!")
                return 'Canceled'
            else:
                logger.info(f"Отмена ордера id : {canceledOrderId}, пара: {symbol} не проведена!")
                TelegramBot.sendText(f"Отмена ордера id : {canceledOrderId}, пара: {symbol} не проведена!")
                return 'Cancel error'
        except Exception as ex:
            logger.error(ex)
            TelegramBot.sendText(str(ex))
            return 'Cancel error'

    def getHistory(self, symbol: str) -> dict:
        """Получение данных об истории ордеров на бирже"""

        tradeClient = TradeClient(api_key=self.userToken[0], secret_key=self.userToken[1])
        result = tradeClient.get_match_result(symbol)
        return result

## Код для автономной отработки модуля (удалить после отработки) ##
if __name__ == '__main__':
    import os
    logsPath = 'D:\\python\\projects\\'  # путь к файлу с логами
    keysPath = 'D:\\python\\projects\\'  # путь к файлу с ключами от аккаунта пользователя
    if os.path.exists(keysPath):
        with open(keysPath, "r") as file:
            keys = file.readline().strip()
            keys = json.loads(keys).get('huobi').split(',')

    def main(coin1, coin2):
        huobiBroker = CryptoBroker('huobi', (keys[0], keys[1]))

        ## Запуск методов getCurrenciesPrice, getBalance для получения данных по валютам и ненулевых балансов пользователя ###
        #task1 = huobiBroker.getCurrenciesPrice(coin1, coin2)
        task2 = huobiBroker.getBalance()
        #task3 = huobiBroker.startTrade(f'{coin1}{coin2}', 'buyLimit', amount=23.0, price=0.45, imitationMode=False)

        #task4 = huobiBroker.getOrderState(930223678200122)
        #task5 = huobiBroker.getOpenOrders('xrpusdt')
        #task6 = huobiBroker.getHistory('xrpusdt')
        print(task2)
        ### Запуск метода startTrade для проверки размещения ордеров (удалить после отработки) ###
        #orderId = huobiBroker.startTrade(result[0], 'buyLimit', amount=23.0, price=0.45)

        ### Запуск метода cancelOrder для проверки отмены ордеров (удалить после отработки) ###
        #huobiBroker.cancelOrder('xrpusdt', 926809345953670, False)
        TelegramBot.sendFile(logsPath)

    main('xrp', 'usdt')


## примеры возвращаемых данных ##

# huobiBroker.getOrderState(930224164968440) = {'status': 'ok', 'data': {
#     'id': 930224164968440,
#     'symbol': 'xrpusdt',
#     'account-id': 50550084,
#     'client-order-id': '',
#     'amount': '23.000000000000000000',
#     'market-amount': '0.0',
#     'price': '0.450000000000000000',
#     'created-at': 1698850725702,
#     'type': 'buy-limit',
#     'field-amount': '0.0',
#     'field-cash-amount': '0.0',
#     'field-fees': '0.0',
#     'finished-at': 0,
#     'updated-at': 1698850725702,
#     'source': 'api',
#     'state': 'submitted',
#     'canceled-at': 0}
#  }
# ####Исполненный ордер на продажу
# {
#     'id': 930223678200122,
#     'symbol': 'xrpusdt',
#     'account-id': 50550084,
#     'client-order-id': '',
#     'amount': '18.350000000000000000',
#     'market-amount': '0.0',
#     'price': '0.597910000000000000',
#     'created-at': 1698852587881,
#     'type': 'sell-limit',
#     'field-amount': '18.350000000000000000',
#     'field-cash-amount': '10.971648500000000000',
#     'field-fees': '0.021943297000000000',
#     'finished-at': 1698852647121,
#     'updated-at': 1698852647121,
#     'source': 'spot-android',
#     'state': 'filled',
#     'canceled-at': 0
# }
########################################################

# huobiBroker.getOpenOrders('xrpusdt') = {
#     'status': 'ok',
#     'data': [{
#         'symbol': 'xrpusdt',
#         'source': 'spot-android',
#         'account-id': 50550084,
#         'amount': '17.000000000000000000',
#         'price': '0.596830000000000000',
#         'created-at': 1698851174131,
#         'client-order-id': '',
#         'filled-amount': '0.0',
#         'filled-cash-amount': '0.0',
#         'filled-fees': '0.0',
#         'id': 930227663575373,
#         'state': 'submitted',
#         'type': 'buy-limit'
#     }]
# }
