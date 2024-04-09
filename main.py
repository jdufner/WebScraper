from datetime import datetime
import logging
import os
from downloader import treewalker

if __name__ == '__main__':
    LOG_PATH:str = './logs'
    now: datetime = datetime.now()
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    logging.basicConfig(filename=f'{LOG_PATH}/{now: %Y-%m-%d_%Hh%Mm%Ss}_main.log',
                        encoding='utf-8',
                        format='%(asctime)s,%(msecs)-3d - %(levelname)-8s - %(filename)s:%(lineno)d - '
                               '%(module)s - %(funcName)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
    logging.info("Los geht's")
    t: treewalker.Treewalker = treewalker.Treewalker()
    t.open('http://www.heise.de/')
