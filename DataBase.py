import json
import logging
import sqlite3
import os

## Принудительное переключение рабочей директории ##
file_path = os.path.realpath(__file__).rsplit('\\', 1)[0]
os.chdir(file_path)

logger = logging.getLogger('CryptoMonkey.DataBase')

class DataBase():
    """Класс взаимодействия с базой данных"""

    def __init__(self, connectionToDB: object, imitationMode: bool):
        self.db = connectionToDB
        self.imitationMode = imitationMode
        self.cursor = self.db.cursor()
        if not self.imitationMode:
            self.table = 'order_table'
        else:
            self.table = 'imitation_order_table'
        self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {self.table} (
            id INTEGER,
            exchange TEXT,
            order_info TEXT
        )""")
        self.db.commit()

    def writeOrderInfo(self, openOrderInfo: dict) -> None:
        """Запись открытого ордера в БД"""

        try:
            info = json.dumps(openOrderInfo)
            exchange = openOrderInfo['exchange']
            id = openOrderInfo['id']
            orders = self.cursor.execute(
                f"SELECT order_info FROM {self.table} WHERE exchange = '{exchange}' AND id = {id}").fetchall()
            if not orders:
                self.cursor.execute(f"INSERT INTO {self.table} VALUES ({id}, '{exchange}', '{info}')")
            else:
                self.cursor.execute(
                    f"UPDATE {self.table} SET order_info = '{info}' WHERE exchange = '{exchange}' AND id = {id}")
            self.db.commit()
        except Exception as ex:
            logger.error(ex)

    def changeOrderInfo(self, newInfo: list) -> None:
        """Изменение статуса ордера в БД"""

        try:
            exchange = newInfo[0]
            id = newInfo[1]
            state = newInfo[2]
            orders = self.cursor.execute(
                f"SELECT order_info FROM {self.table} WHERE exchange = '{exchange}' AND id = {id}").fetchall()
            if not orders:
                return
            newOrderInfo = orders[0][0]
            info = json.loads(newOrderInfo)
            info['state'] = state
            newOrderInfo = json.dumps(info)
            self.cursor.execute(
                f"UPDATE {self.table} SET order_info = '{newOrderInfo}' WHERE exchange = '{exchange}' AND id = {id}")
            self.db.commit()
        except Exception as ex:
            logger.error(ex)

    def readOrderInfo(self, *args) -> list:
        """Чтение ордеров из БД,
        *args может получать ниодного/один/два аргумента по порядку: exchange: str, id: int"""

        try:
            if len(args) == 2:
                exchange = args[0]
                id = args[1]
                orders = self.cursor.execute(
                    f"SELECT order_info FROM {self.table} WHERE exchange = '{exchange}' AND id = {id}").fetchall()
            elif args and type(args[0]) is str:
                exchange = args[0]
                orders = self.cursor.execute(
                    f"SELECT order_info FROM {self.table} WHERE exchange = '{exchange}'").fetchall()
            elif args and type(args[0]) is int:
                id = args[0]
                orders = self.cursor.execute(
                    f"SELECT order_info FROM {self.table} WHERE id = {id}").fetchall()
            else:
                orders = self.cursor.execute(
                    f"SELECT order_info FROM {self.table}").fetchall()
            return orders
        except Exception as ex:
            logger.error(ex)

    def deleteAll(self):
        """Очищение таблицы"""

        self.cursor.execute(f"DELETE FROM {self.table}")


if __name__ == "__main__":
    Json = {"id": 898819183120425, "exchange": "huobi", "symbol": "xrpusdt", "type": "Buy_limit", "amount": 23, "price": 0.45, "state": "Canceled"}
    dataBase = DataBase(sqlite3.connect('database.db'))
    #dataBase.changeOrderInfo(['huobi', 898819183120425, 'Canceled'])
    #dataBase.writeOrderInfo(Json)
    data = dataBase.readOrderInfo('huobi', 898819183120426)
    print(data)
