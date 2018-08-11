# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import sqlite3
import pymysql
from twisted.enterprise import adbapi
import datetime as dt
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class SplashExamplesPipeline(object):
    def process_item(self, item, spider):
        return item


class BookPipeline(object):
    review_rating_map = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5
    }

    def process_item(self, item, spider):
        rating = item.get('review_rating')
        if rating:
            item['review_rating'] = self.review_rating_map[rating]
        return item


class SQLitePipeline(object):

    def open_spider(self, spider):
        db_name = spider.settings.get('SQLITE_DB_NAME', 'scrapy_defaut.db')
        self.db_conn = sqlite3.connect(db_name)
        self.db_cur = self.db_conn.cursor()

    def close_spider(self, spider):
        self.db_conn.commit()
        self.db_conn.close()

    def process_item(self, item, spider):
        self.insert_db(item)
        return item

    def insert_db(self, item):
        values = (
            item['upc'],
            item['name'],
            item['price'],
            item['review_rating'],
            item['review_num'],
            item['stock'],
        )
        sql = 'INSERT INTO books VALUES(?,?,?,?,?,?)'
        self.db_cur.execute(sql, values)


# for signle thread
class MysqlPipeline(object):

    def open_spider(self, spider):
        db = spider.settings.get('MYSQL_DB_NAME', 'dbName')
        host = spider.settings.get('MYSQL_HOST', '192.168.0.101')
        port = spider.settings.get('MYSQL_PORT', 3306)
        user = spider.settings.get('MYSQL_USER', 'li.zhou')
        passwd = spider.settings.get('MYSQL_PASSWORD', 'passwd')

        self.db_conn = pymysql.connect(host=host, port=port, db=db, user=user, passwd=passwd, charset='utf8')
        self.db_cur = self.db_conn.cursor()

    def close_spider(self, spider):
        self.db_conn.commit()
        self.db_conn.close()

    def process_item(self, item, spider):
        self.insert_db(item)
        return item

    def insert_db(self, item):
        values = (
            item['upc'],
            item['name'],
            item['price'],
            item['review_rating'],
            item['review_num'],
            item['stock']
        )
        sql = 'INSERT INTO books VALUES(%s,%s,%s,%s,%s,%s)'
        self.db_cur.execute(sql, values)


# for multiple thread version os mysql
# api: https://twistedmatrix.com/documents/current/core/howto/rdbms.html
class MysqlAsyncPipeline(object):

    def open_spider(self, spider):
        db = spider.settings.get('MYSQL_DB_NAME', 'dbName')
        host = spider.settings.get('MYSQL_HOST', '192.168.0.101')
        port = spider.settings.get('MYSQL_PORT', 3306)
        user = spider.settings.get('MYSQL_USER', 'li.zhou')
        passwd = spider.settings.get('MYSQL_PASSWORD', 'passwd')

        # thread pool, every thread auto commit
        self.dbpool = adbapi.ConnectionPool('pymysql', host=host, port=port, db=db, user=user, passwd=passwd, charset='utf8')

    def close_spider(self, spider):
        self.dbpool.close()

    def process_item(self, item, spider):
        self.dbpool.runInteraction(self.insert_db, item) ### not pass tx ??? A lightweight wrapper for a DB-API 'cursor' object.
        return item

    # tx: A lightweight wrapper for a DB-API 'cursor' object.  the name is customed by user define
    def insert_db(self, tx, item):
        values = (
            item['upc'],
            item['name'],
            item['price'],
            item['review_rating'],
            item['review_num'],
            item['stock']
        )
        sql = 'INSERT INTO books VALUES(%s,%s,%s,%s,%s,%s)'
        tx.execute(sql, values)

dstFile = '/home/zhou-li/crontab/data/stockIndex.hdf'
datasetName = 'stockIndex'
class IndexCrawlPipeline(object):

    def open_spider(self, spider):
        self.hdf = pd.HDFStore(dstFile, 'a', complevel=9, complib='blosc')
        logger.info('IndexCrawlPipeline.open_spider')

    def close_spider(self, spider):
        self.hdf.close()
        logger.info('IndexCrawlPipeline.close_spider')

    def process_item(self, item, spider):
        logger.info('Begin IndexCrawlPipeline.process_item')
        #date = dt.datetime.strptime(dateStr, '%Y-%m-%d')
        date = dt.datetime.strptime(item['date'], '%Y-%m-%d')
        dstDict = {date: [float(item['symbol']), float(item['open']), float(item['high']), float(item['low']), float(item['close']), float(item['volume']), float(item['amount']), float(item['turnoverrate'])]}
        logger.debug('dstDict: \n {}'.format(dstDict))
        columns = ['symbol', 'open', 'high', 'low', 'close', 'volume', 'amount', 'turnoverrate']
        df = pd.DataFrame(columns=columns)
        df = pd.DataFrame.from_dict(dstDict, orient='index')
        df.index.name = 'date'
        df.columns = columns
        logger.debug('df.dtypes: \n {}'.format(df.dtypes))
        logger.debug('df.index: \n {}'.format(df.index))
        logger.debug('df: \n {}'.format(df))
        self.hdf.append(datasetName, df, format='table')
        logger.info('End IndexCrawlPipeline.process_item')
        return item
