from threading import Thread
from tqdm import tqdm
from time import sleep

def list_gene(list):
    for i in tqdm(list):
        yield i

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
    
    def set_callback(self,callback):
        self.callback = callback
        
    def run(self):
        self.__stop__ = False
        for i in range(self.max_threads):
            self.workers.append(worker(self)) 
        for t in self.workers:
            t.start()
        
    def add_task(self,task,task_type):
        if type(task) == type(self.base_task_model):
            if task_type == 0:
                self.queue.append(task)
            elif task_type == 1:
                self.failed_queue.append(task)
        pass    #Invalid task
        
    def get_task(self):
        if len(self.queue) != 0:
            return self.iter.__next__(),0
        elif len(self.failed_queue) != 0:
            return self.failed_queue.pop(),1
        return False,False
        
    def stop(self):
        self.__stop__ = True
            
class worker(Thread):
    def __init__(self,ws,*args,**kw):
        self.ws = ws
        super(worker,self).__init__(*args,**kw)
        
    def run(self):
        while True:
            sleep(self.ws.sleep_func())
            if not self.ws.__stop__:
                current_task,task_type = False
                try:
                    current_task,task_type = ws.get_task()
                except Exception as e:
                    #end
                    pass
                if current_task == False:
                    break
                elif task_type == 0:
                    succeed = current_task.run()
                    if not succeed:
                        self.add_task(current_task,1)
                elif task_type == 1:
                    succeed = current_task.retry()
                    if not succeed:
                        self.add_task(current_task,1)
                        #TODO log,在重试队列中几次失败后放弃
            else:
                break
                
class base_task(object):
    def __init__(self,ws):
        self.ws = ws
        
    def run(self):
        pass
        
    def retry(self):
        pass
            
                
        