#!/usr/bin/env python

import sys, time
from backend import daemon
import itchat
import time
from ipcqueue import posixmq
import logging
import datetime as dt
import threading
import time

logFileDir = "/opt/crontab/IpcToItchat/"
nowDateTime = dt.datetime.now().strftime('%Y%m%d%H%M%S')
pyFilename = sys.argv[0].split('/')[-1].split('.')[0]
logFileName = '{1}_{0}.log'.format(nowDateTime , pyFilename)
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)-8s] [%(asctime)s]: %(message)s',\
    datefmt='%Y-%m-%d %H:%M:%S', filename=logFileDir + logFileName, filemode='w')

class MyDaemon(daemon):
    def run(self):
        logging.info('run begin...')
        q = posixmq.Queue('/ipcmsg')
        itchat.load_login_status(fileDir='/opt/crontab/IpcToItchat/itchat.pkl');
        while True:
            rcvMsg = q.get()
            logging.debug('Get msg: {}'.format(rcvMsg))
            itchat.send(rcvMsg[1], 'filehelper')
            if int(rcvMsg[0]) == 1: # beatheart
                itchat.send(rcvMsg[1], 'filehelper')
            if int(rcvMsg[0]) == 2: # spider 
                for room in itchat.get_chatrooms():
                    nickName = room['NickName']
                    if room['NickName'] == "liuyi":
                        author = itchat.search_chatrooms(userName=room['UserName'])
                        author.send(rcvMsg[1])
                        logging.debug('Send msg: {}'.format(rcvMsg[1]))
        logging.info('run exit')
        

if __name__ == "__main__":
    logging.info('Game start...')
    itchat.auto_login(enableCmdQR=2, hotReload=True)
    daemon = MyDaemon('/tmp/daemon-example.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print("Unknown command")
            sys.exit(2)
        sys.exit(0)
    else:
        print("usage: %s start|stop|restart" % sys.argv[0])
        sys.exit(2)
    logging.info('Game over.')
