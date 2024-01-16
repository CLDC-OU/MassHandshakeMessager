from datetime import datetime as dt
import logging
import os

from src.messager import Messager


logfile = f"logs/{dt.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
if not os.path.exists("logs"):
    os.makedirs("logs")
logging.basicConfig(
    filename=logfile,
    encoding='utf-8',
    level=logging.DEBUG,
    filemode='w',
    format='%(levelname)s:%(asctime)s:[%(module)s] %(message)s'
)
logging.info("Log started")


class Driver:
    def __init__(self):
        self.messager = Messager()

    def run(self):
        self.messager.run()

    def load(self):
        pass


Driver().run()
