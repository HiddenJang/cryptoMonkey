import logging
import asyncio
from huobi.client.account import AccountClient
from huobi.constant import *
from huobi.utils import LogInfo

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

def startTrade(
        exchange:str,
        userToken:tuple,
        currencyData:str,
        orderType: str
) -> dict:

    if exchange == 'huobi':
        account_client = AccountClient(api_key=userToken[0],
                                       secret_key=userToken[1])
        LogInfo.output("====== (SDK encapsulated api) not recommend for low performance and frequence limitation ======")
        accountList = account_client.get_accounts()
        print(accountList)
        # account_balance_list = account_client.get_account_balance()
        # if account_balance_list and len(account_balance_list):
        #     for account_obj in account_balance_list:
        #         account_obj.print_object()


startTrade('huobi',('d896772a-7e580e93-frbghq7rnm-69eb5','b42b5258-2ae7ea40-b299b36e-b8583'), 'btc/usdt', 'buy')