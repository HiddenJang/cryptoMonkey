import requests
import logging

logger = logging.getLogger('CryptoMonkey.TelegramBot')

class TelegramBot():
    """Класс включения и взаимодействия с телеграмм-ботом"""
    messageSwitch = True

    @staticmethod
    def sendText(text: str):
        """Отправка текста"""
        if TelegramBot.messageSwitch:
            try:
                token = "5619069193:AAGNIzLkQUo7mX4aglRXRnvc904C_4jbqCM" #токен бота
                chat_id = "@CryptoMonkey_python_project" #айди или ссылка-приглашение группы в телеграм
                url_req = "https://api.telegram.org/bot" + token + "/sendMessage" + "?chat_id=" + chat_id + "&text=" "Докладываю:\n" + text
                requests.get(url_req)
            except Exception as ex:
                logger.info(f'Ошибка отправки текстового сообщения в телеграмм, {ex}')
            return

    @staticmethod
    def sendImg(pngPath: str):
        """Отправка изображений"""
        if TelegramBot.messageSwitch:
            try:
                token = "5619069193:AAGNIzLkQUo7mX4aglRXRnvc904C_4jbqCM"  # токен бота
                chat_id = "@CryptoMonkey_python_project"  # айди или ссылка-приглашение группы в телеграм
                request_url = "https://api.telegram.org/bot" + token + "/sendMediaGroup"
                params = {"chat_id": chat_id, "media":"""[{"type": "photo", "media": "attach://random-name-1"}]"""}
                files = {"random-name-1": open(f"{pngPath}", "rb")} # ссылка на локальный файл
                requests.post(request_url, params=params, files=files)
            except Exception as ex:
                logger.info(f'Ошибка отправки изображения в телеграмм, {ex}')
            return

    @staticmethod
    def sendFile(filePath: str):
        """Отправка файлов"""
        if TelegramBot.messageSwitch:
            try:
                token = "5619069193:AAGNIzLkQUo7mX4aglRXRnvc904C_4jbqCM"  # токен бота
                chat_id = "@CryptoMonkey_python_project"  # айди или ссылка-приглашение группы в телеграм
                request_url = "https://api.telegram.org/bot" + token + "/sendMediaGroup"
                params = {"chat_id": chat_id, "media":"""[{"type": "document", "media": "attach://random-name-1"}]"""}
                files = {"random-name-1": open(f"{filePath}", "rb")} # ссылка на локальный файл
                requests.post(request_url, params=params, files=files)
            except Exception as ex:
                logger.info(f'Ошибка отправки файла в телеграмм, {ex}')

    @staticmethod
    def botState(var: bool):
        """Установка разрешения на отправку сообщений"""
        TelegramBot.messageSwitch = var
        if var:
            logger.info('Включена отправка сообщений в телеграм')
            TelegramBot.sendText('Бот активирован!Поехали!')
        else:
            logger.info('Выключена отправка сообщений в телеграм')
            TelegramBot.sendText('Бот деактивирован!')
