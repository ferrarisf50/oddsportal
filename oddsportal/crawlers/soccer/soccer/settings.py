from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging



BOT_NAME = 'soccer'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['soccer.spiders']
NEWSPIDER_MODULE = 'soccer.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

ITEM_PIPELINES = ['soccer.pipelines.ResultsItem']

DATABASE = {'drivername': 'postgres',
            'host': 'localhost',
            'port': '5432',
            'username': 'soccer',
            'password': 'soccer',
            'database': 'soccer_db'}
            
            
            
USER_AGENT_LIST = [
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.7 \
         (KHTML, like Gecko) Chrome/16.0.912.36 Safari/535.7',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0) \
       Gecko/16.0 Firefox/16.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 \
       (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10'
]
HTTP_PROXY = 'http://127.0.0.1:8123'
DOWNLOADER_MIDDLEWARES = {
     'soccer.middlewares.RandomUserAgentMiddleware': 400,
     'soccer.middlewares.ProxyMiddleware': 410,
     'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None
    # Disable compression middleware, so the actual HTML pages are cached
}




logger_present = logging.getLogger('present')
logger_absent  = logging.getLogger('absent')
hdlr_present   = logging.FileHandler('present.log')
hdlr_absent    = logging.FileHandler('absent.log')

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr_present.setFormatter(formatter)
hdlr_absent.setFormatter(formatter)

logger_present.addHandler(hdlr_present)
logger_absent.addHandler(hdlr_absent)
logger_present.setLevel(logging.DEBUG)
logger_absent.setLevel(logging.WARNING)



Session = sessionmaker()
engine  = create_engine('postgresql://soccer:soccer@localhost/soccer_db')
Session.configure(bind = engine)
session = Session()
session._model_changes = {}
