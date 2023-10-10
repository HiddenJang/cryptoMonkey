import logging
import asyncio
import aiohttp
from huobi.client.account import AccountClient
from huobi.constant import *
from huobi.client.trade import TradeClient
from huobi.utils import *

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

class cryptoBroker():
    """Класс взаимодействия с критобиржей"""

    def __init__(self, exchange: str, userToken: tuple):
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
                #print(currencyCommonData)
                currencyData["exchange"] = f'{self.exchange}'
                currencyData["pare"] = f'{baseCurrency}/{quoteCurrency}'
                currencyData["price"] = currencyCommonData["tick"]["data"][0]["price"]
                #print(currencyData)
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
                userBalances = []
                for coinBalance in allCoinsBalance:
                    if float(coinBalance["balance"]) > 0:
                        userBalances.append({
                            'currency': coinBalance['currency'],
                            'type': coinBalance['type'],
                            'balance': coinBalance['balance'],
                            'available': coinBalance.get('available')
                        })
                if not userBalances:
                    logger.info("Все спотовые балансы аккаунта пользователя равны нулю")
                print(userBalances)
                return userBalances
            except Exception as ex:
                logger.error(ex)

    async def startTrade(self, currencyData: dict, orderType: str) -> None:
        """Метод размещения ордера на покупку/продажу"""

        symbol = currencyData["pare"].remove("/", "")

        account_id = g_account_id

        trade_client = TradeClient(api_key=g_api_key, secret_key=g_secret_key)
        order_id = trade_client.create_order(symbol=symbol, account_id=account_id, order_type=OrderType.BUY_LIMIT,
                                             source=OrderSource.API, amount=4.0, price=1.292)
        LogInfo.output("created order id : {id}".format(id=order_id))

        canceled_order_id = trade_client.cancel_order(symbol, order_id)
        if canceled_order_id == order_id:
            LogInfo.output("cancel order {id} done".format(id=canceled_order_id))
        else:
            LogInfo.output("cancel order {id} fail".format(id=canceled_order_id))

        order_id = trade_client.create_order(symbol=symbol, account_id=account_id, order_type=OrderType.BUY_MARKET,
                                             source=OrderSource.API, amount=5.0, price=1.292)
        LogInfo.output("created order id : {id}".format(id=order_id))

        order_id = trade_client.create_order(symbol=symbol, account_id=account_id,
                                             order_type=OrderType.SELL_MARKET, source=OrderSource.API, amount=1.77,
                                             price=None)
        LogInfo.output("created order id : {id}".format(id=order_id))

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
    await asyncio.gather(task1, task2)

asyncio.run(main('btc', 'rub'))

