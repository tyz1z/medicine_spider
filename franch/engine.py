from threading import Thread,Lock
from tqdm import tqdm
from time import sleep
import logging

__lock__ = Lock()

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.DEBUG)
# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# FileHandler
file_handler = logging.FileHandler('result.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def list_gene(list):
    for i in tqdm(list):
        yield i

class workshopRuntimeException(Exception):
    def __init__(self,cause):
        self.cause = cause
        Exception.__init__(self,cause)
    
class workshop(object):
    def __init__(self,max_threads,sleep_func):
        self.max_threads = max_threads
        self.sleep_func = sleep_func
        self.queue = []
        self.workers = []
        self.__stop__ = False
        self.base_task_model = base_task(self)
        self.failed_queue = []  #未完成的部分可以考虑序列化
        self.iter = list_gene(self.queue)
        self.__task_limit__ = -1
        self.__debug_mode__ = False
        self.debug_failed_log_path = "debug_failed_log.txt"
    
    #-1:closed
    #num:还可产出的任务数
    def test(self,num,debug = False):
        self.__task_limit__ = num
        self.run(debug = debug)

    def check(self):
        print("tasks:"+self.queue.__str__())
        
    def run(self,debug = False):
        self.__stop__ = False
        self.__debug_mode__ = debug
        for i in range(self.max_threads):
            self.workers.append(worker(self)) 
        for t in self.workers:
            t.start()
        for t in self.workers:
            t.join()
        
    def add_task(self,task,task_type):
        if task_type == 0:
            self.queue.append(task)
        elif task_type == 1:
            self.failed_queue.append(task)
        pass    #Invalid type
        
    def get_task(self):
        if self.__task_limit__ >= 0:
            if self.__task_limit__ >0:
                self.__task_limit__ -= 1
            else:
                return False,False
        __lock__.acquire()
        try:
            task = self.iter.__next__()
            return task,0
        except Exception as e:
            return False,False
        finally:
            __lock__.release()
        if len(self.failed_queue) != 0:
            return self.failed_queue.pop(),1
        return False,False
        
    def stop(self):
        self.__stop__ = True

#要不要加一个失败中断型debug？        
class worker(Thread):
    def __init__(self,ws,*args,**kw):
        self.ws = ws
        super(worker,self).__init__(*args,**kw)
        
    def debug(self):
        while True:
            sleep(self.ws.sleep_func())
            if self.ws.__stop__:
                break
            current_task,task_type = self.ws.get_task()
            if current_task == False:
                break
            succeed = current_task.real_run() #没有retry
            if not succeed:
                logger.info(str(current_task.cause['token'])+" :"+current_task.cause['info'])
                with open(self.ws.debug_failed_log_path,'a',encoding="utf-8") as f:
                    #记录失败凭证
                    f.write(str(current_task.cause['token'])+'\n')
        
    def work(self):
        while True:
            sleep(self.ws.sleep_func())
            if self.ws.__stop__:
                break
            current_task,task_type = self.ws.get_task()
            if current_task == False:
                break
            elif task_type == 0:
                succeed = current_task.real_run()
                if not succeed:
                    self.ws.add_task(current_task,1)
                    #TODO log cause
            elif task_type == 1:
                succeed = current_task.real_run(retry = True)
                if not succeed:
                    self.ws.add_task(current_task,1)
                    #TODO log cause,在重试队列中几次失败后放弃
                    
    def run(self):
        if self.ws.__debug_mode__:
            self.debug()
        else:
            self.work()
                
class base_task(object):
    def __init__(self,ws):
        self.ws = ws
        self.cause = {"token":"","info":""}
        
    #主动异常收束
    #用异常来传递信息主要是因为跨层
    #到此截止是因为一个Task是一个原子化事务，事务异常不再向上影响到worker
    def real_run(self,retry = False):
        try:
            if retry:
                return self.retry()
            else:
                return self.run()
        except workshopRuntimeException as e:
            self.cause['info'] = e.cause
            return False
        except Exception as e:
            self.cause['info'] = str(e)
        
    def run(self):
        pass
        
    def retry(self):
        return self.run()
            
                
        