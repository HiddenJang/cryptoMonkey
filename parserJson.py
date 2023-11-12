import aiohttp
import asyncio
import logging

logger = logging.getLogger('CryptoMonkey.parserJson')

async def getMyfinData(session, currency):
    url = f'https://api.coinbase.com/v2/exchange-rates?currency={currency}'
    headers = {
        'authority': 'api.coinbase.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        # 'cookie': 'cb_dm=b0a87ec2-7f58-4d34-a8f0-be995286125c; coinbase_device_id=9920925c-ba98-4c30-909a-1f4dea7abd53; advertising_sharing_allowed={%22value%22:true}; _fbp=fb.1.1693757962513.65855692; cm_default_preferences={%22region%22:%22DEFAULT%22%2C%22consent%22:[%22necessary%22%2C%22performance%22%2C%22functional%22%2C%22targeting%22]}; _gid=GA1.2.1912383428.1694093377; _dpm_ses.268f=*; _dpm_id.268f=c2289483-900a-4c53-8558-c5c9aa38a778.1694094203.1.1694094203.1694094203.cf98f5b6-1079-4028-a46a-be4d82116246; _ga_90YJL6R0KZ=GS1.1.1694093377.5.1.1694094203.16.0.0; _ga=GA1.1.1426099038.1693757949; _ga_W5Z1BRK56L=GS1.2.1694093377.5.1.1694094203.0.0.0; __cf_bm=nu1UrM4BXFIOQhq.0Lh20.7yWksWURniHwEZI0YpY_Q-1694090605-0-AdIUa7sEahXZhzfXetn/WeCgUnD4wuGihx8ioDTaPW8t9m0ZOnzkUW4aHaPA5gYQT2te75/Po8u5sWDQK3SgCXo=; _ga_1X60WF4D7F=GS1.1.1694094752.1.1.1694094832.0.0.0',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    try:
        async with session.get(url, headers=headers) as response:
            return await response.json()
    except Exception as ex:
        logger.error(ex)

async def getKucoinData(session, currency):
    # url = 'https://api.kucoin.com/api/v1/market/orderbook/level1?symbol=BTC-USDT'
    url = f'https://api.kucoin.com/api/v1/prices?base={currency}'
    headers = {
        'authority': 'www.kucoin.com',
        'accept': '*/*',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        # 'cookie': '__cfruid=65b6dc79984efb451b83bb1dccbc95dc549f2a9d-1693844755; __cf_bm=P5ukn19P5U1TKIkxEUd3E0z.KCM0KS9NT.LaBG0z60o-1694095340-0-AeUhV71lqaS3xFM3a7RnrNF6p2sEBbitCO34wo1AAgkc/y+mIDcCgp7hpvlhivkRv9Csh69xa3ZMhxqeQi1Yj8U=; _gid=GA1.2.175346202.1694099026; .thumbcache_722636655709b1ebe7ba38ddab226e34=; smidV2=20230907190350d95060e78201f87d60044e8ed0244886003a164c7721e2550; as_uzZo5y=3a31d4e5006afd034a43bbe44db277ae5534031aa93783419456815ef558ddb36e0ba6f5; x-bullet-token=2neAiuYvAU5cbMXpmsXD5OJlewXCKryg8dSpDCgag8ZwbZpn3uIHi0A1AOtpCibAwoXOiOG0Q0HO9PWcZ4kF86RDa3sBu5dWX_bE7WTUf_A3AapFEfjsxaqRyqznCVt1whuoNZhpWWExTqzT-X-8i_1mjIh2D-pO.UqSUqEJulko8h7e8AQCzuA==; _ga_YHWW24NNH9=GS1.1.1694099026.2.1.1694099433.58.0.0; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218a60305a8b567-030cec43b46dd84-26031f51-1049088-18a60305a8c21d%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThhNjAzMDVhOGI1NjctMDMwY2VjNDNiNDZkZDg0LTI2MDMxZjUxLTEwNDkwODgtMThhNjAzMDVhOGMyMWQifQ%3D%3D%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218a60305a8b567-030cec43b46dd84-26031f51-1049088-18a60305a8c21d%22%7D; _ga=GA1.2.51242321.1693830896; _gat_UA-46608064-1=1; AWSALB=0HJTgB6l79i3SXhKVWfiiKoYapnYzBQBeBiJ0HOB7O53lM2abQdEF/wxtKhAdH6o0XCBLEoL2NnrGwK9muVAmhTXl2S7HQHDyJ5jq75xwO2LRxn7sgmwYjEQ8GVl; AWSALBCORS=0HJTgB6l79i3SXhKVWfiiKoYapnYzBQBeBiJ0HOB7O53lM2abQdEF/wxtKhAdH6o0XCBLEoL2NnrGwK9muVAmhTXl2S7HQHDyJ5jq75xwO2LRxn7sgmwYjEQ8GVl',
        'if-modified-since': 'Thu, 07 Sep 2023 08:36:11 GMT',
        'referer': 'https://www.kucoin.com/sw.js',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    try:
        async with session.get(url, headers=headers) as response:
            cryptoDict = (await response.json()).get('data')
            return cryptoDict
    except Exception as ex:
        logger.error(ex)

async def getCoinbaseData(session, currency):
    # url = 'https://api.coinbase.com/v2/prices/BNB-USD/sell/'
    url = f'https://api.coinbase.com/v2/exchange-rates?currency={currency}'
    headers = {
        'authority': 'api.coinbase.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'max-age=0',
        # 'cookie': 'cb_dm=b0a87ec2-7f58-4d34-a8f0-be995286125c; coinbase_device_id=9920925c-ba98-4c30-909a-1f4dea7abd53; advertising_sharing_allowed={%22value%22:true}; _fbp=fb.1.1693757962513.65855692; cm_default_preferences={%22region%22:%22DEFAULT%22%2C%22consent%22:[%22necessary%22%2C%22performance%22%2C%22functional%22%2C%22targeting%22]}; _gid=GA1.2.1912383428.1694093377; _dpm_ses.268f=*; _dpm_id.268f=c2289483-900a-4c53-8558-c5c9aa38a778.1694094203.1.1694094203.1694094203.cf98f5b6-1079-4028-a46a-be4d82116246; _ga_90YJL6R0KZ=GS1.1.1694093377.5.1.1694094203.16.0.0; _ga=GA1.1.1426099038.1693757949; _ga_W5Z1BRK56L=GS1.2.1694093377.5.1.1694094203.0.0.0; __cf_bm=nu1UrM4BXFIOQhq.0Lh20.7yWksWURniHwEZI0YpY_Q-1694090605-0-AdIUa7sEahXZhzfXetn/WeCgUnD4wuGihx8ioDTaPW8t9m0ZOnzkUW4aHaPA5gYQT2te75/Po8u5sWDQK3SgCXo=; _ga_1X60WF4D7F=GS1.1.1694094752.1.1.1694094832.0.0.0',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }
    try:
        async with session.get(url, headers=headers) as response:
            cryptoDict = (await response.json()).get('data').get('rates')
            for key, coin in zip(cryptoDict.keys(), cryptoDict):
                cryptoDict[key] = 1 / float(cryptoDict.get(key))
            return cryptoDict
    except Exception as ex:
        logger.error(ex)

async def getAllData(session, currency):
    tasks = []
    tasks.append(asyncio.create_task(getMyfinData(session, currency)))
    tasks.append(asyncio.create_task(getKucoinData(session, currency)))
    tasks.append(asyncio.create_task(getCoinbaseData(session, currency)))
    results = await asyncio.gather(*tasks)
    return results

async def startParsing(currency):
    async with aiohttp.ClientSession() as session:
        parsData = await getAllData(session, currency)
        return parsData

if __name__ == '__main__':
    crypto = asyncio.run(startParsing('RUB'))

