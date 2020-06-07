"""
@File   :web_server.py
@Author :JohsuaWu1997
@Date   :13/03/2020
"""
import asyncio
import websockets
import json
import pymysql
import importlib


def sql_fetch_json(cursor: pymysql.cursors.Cursor):
    """
    Convert the pymysql SELECT result to json format
    :param cursor:
    :return:
    """
    keys = []
    for column in cursor.description:
        keys.append(column[0])
    key_number = len(keys)

    json_data = []
    for row in cursor.fetchall():
        item = dict()
        for q in range(key_number):
            item[keys[q]] = str(row[q])
        json_data.append(item)
    return json.dumps(json_data)


async def get_list(websocket, path):
    userDB = pymysql.connect(user='root', password='123456', database='userdb', use_unicode=True)
    cursor = userDB.cursor()
    cursor.execute('select * from trade_list')
    trade_list = sql_fetch_json(cursor)
    cursor.close()
    await websocket.send(trade_list)


async def trade(websocket, path):
    msg = await websocket.recv()
    print('msg:', msg)
    if not msg == '':
        re = msg.split(',')
        if re[0].strip().endswith('test'):
            module = importlib.import_module('modules.' + re[0].split('.')[0])
            broker = module.Strategy(re[1], websocket)
            await broker.test()
        elif re[0].strip().endswith('replay'):
            module = importlib.import_module('modules.replay')
            broker = module.Replay(re[1], websocket)
            await broker.test()
        else:
            module = importlib.import_module('modules.' + re[0])
            broker = module.Strategy(re[1], websocket)
            await broker.run()


def main():
    list_server = websockets.serve(get_list, "localhost", 12000)
    trade_server = websockets.serve(trade, "localhost", 12001)
    asyncio.get_event_loop().run_until_complete(list_server)
    asyncio.get_event_loop().run_until_complete(trade_server)
    asyncio.get_event_loop().run_forever()


if __name__ == '__main__':
    main()
