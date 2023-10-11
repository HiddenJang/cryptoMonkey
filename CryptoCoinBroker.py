import logging
import asyncio
import aiohttp
from huobi.client.account import AccountClient
from huobi.constant import *
from huobi.client.trade import TradeClient
from huobi.utils import *
from TelegramBot import TelegramBot
from time import sleep

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
logger = logging.getLogger('CryptoMonkey.CryptoCoinBroker')

TelegramBot.botState(True)
TelegramBot.sendText('!!!ВНИМАНИЕ!!!\nПроводится проверка автоматического выставления ордера и'
                     'алгоритма отмены ордера по требованию пользователя!!!')
class cryptoBroker():
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
                accountList = account_client.get_accounts()
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


    async def getCurrenciesInfo(
            self,
            baseCurrency: str,
            quoteCurrency: str
    ) -> dict:
        """Метод получения данных от выбранной криптобиржи по выбранным валютам"""

        currencyData = {}
        if self.exchange == 'huobi':
            url = f'https://api.huobi.pro/market/trade?symbol={baseCurrency}{quoteCurrency}'  ##текущая цена криптовалюты
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        currencyCommonData = await response.json()
                currencyData["exchange"] = f'{self.exchange}'
                currencyData["pare"] = f'{baseCurrency}/{quoteCurrency}'
                currencyData["price"] = currencyCommonData["tick"]["data"][0]["price"]
                #TelegramBot.sendText(f'---Данные переменной currencyData метода getCurrenciesInfo:---\n{currencyData}\n')
                logger.error('Данные по выбранной валютной паре успешно получены!')
                TelegramBot.sendText('Данные по выбранной валютной паре успешно получены!')
                return currencyData
            except Exception as ex:
                logger.error(ex)
                TelegramBot.sendText(str(ex))


    async def getBalance(self) -> list:
        """Метод получения ненулевых балансов пользователя"""

        logger.info(f"Запущена функция получения баланса биржи {self.exchange}.")
        TelegramBot.sendText(f"Запущена функция получения баланса биржи {self.exchange}.")
        if self.exchange == 'huobi':
            accountId = self.getAccountId()
            account_client = AccountClient(api_key=self.userToken[0], secret_key=self.userToken[1])
            try:
                ### Получаем все ненулевые балансы в аккаунте пользователя ###
                allCoinsBalance = account_client.get_balance(accountId)
                userBalances = [accountId]
                for coinBalance in allCoinsBalance:
                    if float(coinBalance.get("balance")) > 0:
                        userBalances.append({
                            'currency': coinBalance['currency'],
                            'type': coinBalance['type'],
                            'balance': coinBalance['balance'],
                            'available': coinBalance.get('available')
                        })
                if not userBalances:
                    logger.info("Все спотовые балансы аккаунта пользователя равны нулю")
                    TelegramBot.sendText("Все спотовые балансы аккаунта пользователя равны нулю")
                #TelegramBot.sendText(f'---Данные переменной userBalances метода getBalance---\n{userBalances}\n')
                logger.info("Все спотовые ненулевые балансы аккаунта пользователя успешно получены!")
                TelegramBot.sendText("Все спотовые ненулевые балансы аккаунта пользователя успешно получены!")
                return userBalances
            except Exception as ex:
                logger.error(ex)
                TelegramBot.sendText(str(ex))


    def startTrade(
            self,
            currencyData: dict,
            orderType: str,
            amount: float,
            price: float  # None если выставляется ордер по рыночной цене (buyMarket или sellMarket)
    ) -> int:
        """Метод размещения ордера на покупку/продажу"""

        symbol = currencyData["pare"].replace("/", "")
        accountId = self.getAccountId()
        ## Выставление ордера по лимитной цене покупаемой валюты ##
        if orderType == 'buyLimit':
            type = "Покупка_лимитная"
            orderType = OrderType.BUY_LIMIT
        elif orderType == 'sellLimit':
            type = "Продажа_лимитная"
            orderType = OrderType.SELL_LIMIT

        ## Выставление ордера по рыночной цене покупаемой валюты ##
        elif orderType == 'buyMarket':
            type = "Покупка_рыночная"
            orderType = OrderType.BUY_MARKET
        elif orderType == 'sellMarket':
            type = "Продажа_рыночная"
            orderType = OrderType.SELL_MARKET

        try:
            tradeClient = TradeClient(api_key=self.userToken[0], secret_key=self.userToken[1])
            orderId = tradeClient.create_order(symbol=symbol, account_id=accountId, order_type=orderType,
                                                 source=OrderSource.API, amount=amount, price=price)
            logger.info(f"Размещен ордер id : {orderId}, {type}, пара: {currencyData['pare']}!")
            TelegramBot.sendText(f"Размещен ордер id : {orderId}, {type}, пара: {currencyData['pare']}!")
            return orderId
        except Exception as ex:
            logger.error(ex)
            TelegramBot.sendText(str(ex))


    def cancelOrder(
            self,
            currencyData: dict,
            orderId: str,
    ) -> None:
        """Метод отмены выставленного ордера"""

        symbol = currencyData["pare"].replace("/", "")
        try:
            tradeClient = TradeClient(api_key=self.userToken[0], secret_key=self.userToken[1])
            canceledOrderId = tradeClient.cancel_order(symbol, orderId)
            if canceledOrderId == orderId:
                logger.info(f"Отмена ордера id : {canceledOrderId}, пара: {currencyData['pare']} проведена успешно!")
                TelegramBot.sendText(f"Отмена ордера id : {canceledOrderId}, пара: {currencyData['pare']} проведена успешно!")
            else:
                logger.info(f"Отмена ордера id : {canceledOrderId}, пара: {currencyData['pare']} не проведена!")
                TelegramBot.sendText(f"Отмена ордера id : {canceledOrderId}, пара: {currencyData['pare']} не проведена!")
        except Exception as ex:
            logger.error(ex)
            TelegramBot.sendText(str(ex))

## Код для автономной отработки модуля (удалить после отработки) ##
import os
logsPath = 'D:\\Pasha\\python\\projects\\cryptoMonkey\\Logs.txt'  # путь к файлу с логами
keysPath = 'D:\\Pasha\\python\\projects\\user_data.txt'  # путь к файлу с ключами от аккаунта пользователя
if os.path.exists(keysPath):
    with open(keysPath, "r") as file:
        keys = file.readline().strip().split(' ')

async def main(coin1, coin2):
    huobiBroker = cryptoBroker('huobi', (keys[0], keys[1]))
    task1 = asyncio.create_task(huobiBroker.getCurrenciesInfo(coin1, coin2))
    task2 = asyncio.create_task(huobiBroker.getBalance())
    result = await asyncio.gather(task1, task2)
    print(result)
    ### Запуск метода startTrade для проверки размещения ордеров (удалить после отработки) ###
    orderId = huobiBroker.startTrade(result[0], 'buyLimit', amount=23.0, price=0.45)

    sleep(10)
    ### Запуск метода cancelOrder для проверки отмены ордеров (удалить после отработки) ###
    huobiBroker.cancelOrder(result[0], orderId)
    TelegramBot.sendFile(logsPath)

asyncio.run(main('xrp', 'usdt'))

