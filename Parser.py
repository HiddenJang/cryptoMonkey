import aiohttp
import asyncio
import logging

def init_logger(name):
    """Инициализация логгера, убрать после разработки главного модуля"""
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

## создание и инициализация логгера ##
init_logger('CryptoMonkey')
logger = logging.getLogger('CryptoMonkey.Parser')


async def startParsing(exchange: str, baseCurrency: str, quoteCurrency: str) -> dict:
    """Функция получения данных от выбранной криптобиржи и выбранным валютам"""
    if exchange == 'huobi':
        url = f'https://api.huobi.pro/market/trade?symbol={baseCurrency}{quoteCurrency}' ##текущая цена криптовалюты
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    currencyData = await response.json()
            return currencyData
        except Exception as ex:
            logger.error(ex)

## для проверки работы модуля ##
currencyData = asyncio.run(startParsing('huobi', 'btc', 'rub'))
print(currencyData)