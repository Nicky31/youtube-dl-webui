#!/usr/bin/env python
# -*- coding: utf-8 -*-

import youtube_dl

from multiprocessing import Process
from time import time
from copy import deepcopy

WQ_DICT = {'from': 'worker'}


class ydl_hook(object):
    def __init__(self, tid, wqueue):
        self.tid = tid
        self.wq = wqueue


    def dispatcher(self, d):
        v = {'HOOK': d}
        self.wq.put(v)


class log_filter(object):
    def __init__(self, tid, wqueue):
        self.tid = tid
        self.wq = wqueue
        self.wqd = deepcopy(WQ_DICT)
        self.wqd['tid'] = self.tid
        self.wqd['msgtype'] = 'log'
        self.data = {'time': None, 'type': None, 'msg': None}
        self.wqd['data'] = self.data


    def debug(self, msg):
        self.data['time'] = int(time())
        self.data['type'] = 'debug'
        self.data['msg'] = msg
        self.wq.put(self.wqd)


    def warning(self, msg):
        self.data['time'] = int(time())
        self.data['type'] = 'warning'
        self.data['msg'] = msg
        self.wq.put(self.wqd)


    def error(self, msg):
        self.data['time'] = int(time())
        self.data['type'] = 'error'
        self.data['msg'] = msg
        self.wq.put(self.wqd)


class Worker(Process):
    def __init__(self, tid, wqueue, param=None, ydl_opts=None, first_run=False):
        super(Worker, self).__init__()
        self.tid = tid
        self.wq = wqueue
        self.param = param
        self.url = param['url']
        self.ydl_opts = ydl_opts
        self.first_run = first_run
        self.log_filter = log_filter(tid, self.wq)
        self.ydl_hook = ydl_hook(tid, self.wq)


    def intercept_ydl_opts(self):
        self.ydl_opts['logger'] = self.log_filter
        self.ydl_opts['progress_hooks'] = [self.ydl_hook.dispatcher]


    def run(self):
        self.intercept_ydl_opts()

        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            if self.first_run:
                info_dict = ydl.extract_info(self.url, download=False)
                wqd = deepcopy(WQ_DICT)
                wqd['tid'] = self.tid
                wqd['msgtype'] = 'info_dict'
                wqd['data'] = info_dict
                self.wq.put(wqd)

            print('start downloading ...')
            ydl.download([self.url])


    def stop(self):
        print('Terminating Process ...')
        self.terminate()
        self.join()

