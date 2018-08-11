from scrapy.exporters import BaseItemExporter
import pandas as pd
import datetime as dt
import logging

logger = logging.getLogger(__name__)

datasetName = 'stockIndex'
class HdfItemExporter(BaseItemExporter):

    def __init__(self, file, **kwargs):
        self._configure(kwargs, dont_fail=True)
        self.file = file
        self.hdf = pd.HDFStore(self.file.name, 'a', complevel=9, complib='blosc')

    def start_exporting(self):
        pass

    def finish_exporting(self):
        self.hdf.close()

    def export_item(self, item):
        logger.info('Begin HdfItemExporter.export_item')
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
        logger.info('End  HdfItemExporter.export_item')
        return item

