from collections import namedtuple
import threading
import time
import signal
import sys
import types
import sys

class Channel(object):
    def __init__(self,name='default'):
        self.name = name
        self.__stop = False
        self.__items = []
        self._jobs = 0
        self.__lock = threading.Lock()
        #signal.signal(signal.SIGINT, self.signal_handler)

    def signal_handler(self,sig,frame):
        self.__stop = True
        sys.exit(0)

    def append(self,*items):
        with self.__lock: self._jobs += 1
        self.__items.append(items)

    def pop(self):
        try:
            return True, self.__items.pop(0)
        except IndexError:
            return False, None

    def __str__(self):
        return str(self.__items)

    def __len__(self):
        return len(self.__items)

    def open(self):
        return not self.__stop

    def wait(self):
        while self._jobs > 0:
            print(self._jobs, self.__items, self.name)
            time.sleep(0.1)

    def close(self):
        self.__stop = True


result = namedtuple("Result","func ret args channel wid")

def _worker(wid,target,channel,lock,callback=None):
    while( channel.open() ):
            ok, args = channel.pop()
            if not ok: time.sleep(0.50); continue

            try:
                val = target(*args)
                with lock: channel._jobs -= 1
            except Exception as e:
                with lock: channel._jobs -= 1
                val = None
                print(e)

            if type(callback) == types.FunctionType:
                callback(result(wid= wid, channel= channel,
                            func   = target,
                            args   = args,
                            ret    = val,
                        ))

def workers(target,channel,count=5,callback=None):
    for _id in range(1,count+1):
        threading.Thread(target=_worker,args=(_id,target,channel,threading.Lock(),callback,)).start()
