#!/usr/bin/python

import os
import time
from multiprocessing import Pipe, Event, Manager
from killerbeewids.trunk.utils import KBLogUtil

class BaseDronePlugin(object):
    def __init__(self, interfaces, channel, drone):
        #TODO: add interface validation
        self.interfaces = interfaces
        self.kb = None
        self.channel = channel
        self.drone = drone
        self.childprocesses = []
        self.tasks = {}
        self.done_event = Event()
        self.task_update_event = Event()
        self.timeout = 5 
        self.status = True
        self.active = True
        self.desc = None
        self.pid = os.getpid()
        self.logutil = KBLogUtil(self.drone)

    def info(self):
        info = {}
        info['desc'] = self.desc
        info['pid'] = self.pid
        info['status'] = self.status
        info['active'] = self.active
        info['processes'] = list(({'desc':process.desc, 'pid':process.pid} for process in self.childprocesses))
        info['tasks'] = list(({'uuid': task[0], 'parameters':task[1] } for task in self.tasks.items()))
        return info

    def shutdown(self):
        self.logutil.log(self.desc, 'Initiating shutdown', self.pid)
        self.done_event.set()
        for process in self.childprocesses:
            if process.is_alive():
                process.join(self.timeout)
                if process.is_alive():
                    process.terminate()
                    time.sleep(self.timeout)
                    if process.is_alive():
                        raise Exception("Failed to terminate process")
        self.active = False
        #self.kb.plugin = None
        self.kb.active = False
        self.logutil.log(self.desc, 'Successful shutdown', self.pid)

    def task(self, uuid, data):
        '''
        overwrite this function
        '''
    def detask(self, uuid):
        '''
        overwrite this function
        '''



