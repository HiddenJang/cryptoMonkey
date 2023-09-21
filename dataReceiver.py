import aiohttp
import asyncio
import logging
import requests

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
logger = logging.getLogger('CryptoMonkey.dataReceiver')

url = 'https://api.huobi.pro/market/tickers'
url = 'https://api.huobi.pro/v1/common/symbols'
async def startParsing():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                parsData = (await response.json())
        return parsData
    except Exception as ex:
        logger.error(ex)

result = asyncio.run(startParsing())
# for coin in result:
#     #print(coin.get('symbol'))
#     if coin.get('symbol') == 'btcusd':
#         print(coin)
print(result)