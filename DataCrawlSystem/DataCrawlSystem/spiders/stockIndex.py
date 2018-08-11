# -*- coding: utf-8 -*-
import scrapy
from scrapy_splash import SplashRequest
import logging
from ..items import DatacrawlsystemItem
from ipcqueue import posixmq
import time

logger = logging.getLogger(__name__)

lua_script='''
function main(splash)
    splash:go(splash.args.url)
    splash:wait(10)
    return splash:html()
end
'''
# modify splash:wait(30) will get 504 http error, why???

class StockindexSpider(scrapy.Spider):
    name = 'stockIndex'
    indexCodeList = ['000001.SH', '000016.SH', '000300.SH', '000905.SH', '399001.SZ', '399006.SZ']
    start_urls = ['http://quote.eastmoney.com/zs' + code[0:6] + '.html' for code in indexCodeList]
    urlCodeDict = dict(zip(start_urls, indexCodeList))
    # connect to system msg queue
    q = posixmq.Queue('/ipcmsg')
    logger.debug(' 11111111 uurlCodeDict= {}'.format(urlCodeDict))

    def start_requests(self):
        for url in self.start_urls:
            logger.info('request url = {}'.format(url))
            #yield SplashRequest(url, callback=self.parse_test, args={'images':0, 'timeout':10})
            symbol = int(self.urlCodeDict[url][0:6])
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True, meta={
                'symbol': symbol,
                'oriUrl': url,
                'splash': {
                    'args': {
                        # set rendering arguments here
                        'html': 1,
                        'lua_source': lua_script
                    },
                    'cache_args': ['lua_source'],
                    'endpoint': 'execute',
                }
            })
            logger.info(' 11111111 url = {}'.format(url))

    def parse(self, response):
        item = DatacrawlsystemItem()
        item['date'] = response.xpath('//*[@id="hqday"]/text()').re_first('\d+\-\d+\-\d+')
        dateTime = response.xpath('//*[@id="hqday"]/text()').extract_first()
        indexName = response.xpath('//*[@id="name"]/text()').extract_first()
        item['symbol'] = response.meta["symbol"]
        item['open'] = response.xpath('//*[@id="rgt2"]/text()').extract_first()
        item['high'] = response.xpath('//*[@id="rgt3"]/text()').extract_first()
        item['low']  = response.xpath('//*[@id="rgt4"]/text()').extract_first()
        item['close'] = response.xpath('//*[@id="rgt1"]/text()').extract_first()
        item['change'] = response.xpath('//*[@id="rgt5"]/text()').re_first('\-?\d*\.?\d+')
        volume = response.xpath('//*[@id="rgt7"]/text()').re_first('\d+')
        volumeOrig = response.xpath('//*[@id="rgt7"]/text()').extract_first()
        logger.debug('volume = {}, volumeOrig = {}'.format(volume, volumeOrig))
        item['volume'] = int(volume) * 10000 * 100
        amount = response.xpath('//*[@id="rgt8"]/text()').re_first('\d+')
        amountOrig = response.xpath('//*[@id="rgt8"]/text()').extract_first()
        logger.debug('amount = {}, amountOrig = {}'.format(amount, amountOrig))
        item['amount'] = int(amount) * 100000000
        item['turnoverrate'] = response.xpath('//*[@id="rgt9"]/text()').re_first('\-?\d*\.?\d+')
        item['change_5'] = response.xpath('//*[@id="rgt17"]/text()').re_first('\-?\d*\.?\d+')
        item['change_20'] = response.xpath('//*[@id="rgt18"]/text()').re_first('\-?\d*\.?\d+')
        item['change_60'] = response.xpath('//*[@id="rgt19"]/text()').re_first('\-?\d*\.?\d+')
        item['change_year'] = response.xpath('//*[@id="rgt20"]/text()').re_first('\-?\d*\.?\d+')

        # check data nonetype 
        for element in item.keys():
            if item[element] is None:
                logger.error('Item: {} is None, request again.'.format(element))
                logger.info('item: {}'.format(item))
        # send wechat message
        sendMsg = indexName + ", " + dateTime + '\n'
        for element in item.keys():
            if element == 'volume':
                sendMsg = sendMsg + element + ": " + volumeOrig + " , " 
            elif element == 'amount':
                sendMsg = sendMsg + element + ": " + amountOrig + " , " 
            else:
                sendMsg = sendMsg + element + ": " + str(item[element]) + " , " 
        logger.info('sendMsg: {}'.format(sendMsg))
        self.q.put([2, sendMsg])
        #if (float(item['change']) < -2) or (float(item['change_5']) < -8) or (float(item['change_20']) < -15):
        #    self.q.put([2, sendMsg])
        time.sleep(8)
        return item
