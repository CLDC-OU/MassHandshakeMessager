from datetime import datetime as dt
import logging


logfile = f"logs/{dt.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
logging.basicConfig(
    filename=logfile,
    encoding='utf-8',
    level=logging.DEBUG,
    filemode='w',
    format='%(levelname)s:%(asctime)s:[%(module)s] %(message)s'
)
logging.info("Log started")


