import logging
import asyncio
import aiohttp
from huobi.client.account import AccountClient
from huobi.constant import *
from huobi.client.trade import TradeClient
from huobi.utils import *
from TelegramBot import TelegramBot

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

TelegramBot.sendText('Проверка криптобота. Криптобот на связи!')

class cryptoBroker():
    """Класс взаимодействия с критобиржей"""

    def __init__(
            self,
            exchange: str,
            userToken: tuple
    ):
        self.exchange = exchange
        self.userToken = userToken

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
                print(f'###  Данные переменной currencyData метода getCurrenciesInfo  ###\n{currencyData}\n')

                ### Запуск метода startTrade для проверки размещения ордеров (удалить после отработки) ###
                #self.startTrade(50550084, currencyData, 'buyLimit', amount=22.0, price=0.46)

                return currencyData
            except Exception as ex:
                logger.error(ex)

    async def getBalance(self) -> list:
        """Метод получения ненулевых балансов пользователя"""

        logger.info(f"Запущена функция получения баланса биржи {self.exchange}.")
        if self.exchange == 'huobi':
            account_client = AccountClient(api_key=self.userToken[0], secret_key=self.userToken[1])
            try:
                ### Получаем id спотового аккаунта пользователя ###
                accountId = None
                accountList = account_client.get_accounts()
                for account in accountList:
                    if account.get('type') == 'spot':
                        accountId = account.get('id')
                        break
                if not accountId:
                    logger.error("Не удалось получить id спотового аккаунта пользователя")
                    return []

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
                print(f'###  Данные переменной userBalances метода getBalance  ###\n{userBalances}\n')
                return userBalances
            except Exception as ex:
                logger.error(ex)

    def startTrade(
            self,
            accountId: int,
            currencyData: dict,
            orderType: str,
            amount: float,
            price: float  # None если выставляется ордер по рыночной цене (buyMarket или sellMarket)
    ) -> None:
        """Метод размещения ордера на покупку/продажу"""

        symbol = currencyData["pare"].replace("/", "")

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
            trade_client = TradeClient(api_key=self.userToken[0], secret_key=self.userToken[1])
            order_id = trade_client.create_order(symbol=symbol, account_id=accountId, order_type=orderType,
                                                 source=OrderSource.API, amount=amount, price=price)
        except Exception as ex:
            print(ex)
        logger.info(f"Размещен ордер id : {order_id}, {type}, пара: {currencyData['pare']}")


## Код для автономной отработки модуля (удалить после отработки) ##
import os
keysPath = 'D:\\Pasha\\python\\projects\\user_data.txt'  # путь к файлу с ключами от аккаунта пользователя
if os.path.exists(keysPath):
    with open(keysPath, "r") as file:
        keys = file.readline().strip().split(' ')

async def main(coin1, coin2):
    huobiBroker = cryptoBroker('huobi', (keys[0], keys[1]))
    task1 = asyncio.create_task(huobiBroker.getCurrenciesInfo(coin1, coin2))
    task2 = asyncio.create_task(huobiBroker.getBalance())
    result = await asyncio.gather(task1, task2)




asyncio.run(main('xrp', 'usdt'))

