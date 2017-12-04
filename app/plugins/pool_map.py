# -*- coding: utf-8 -*-
from multiprocessing.dummy import Pool as ThreadPool
import Queue


class MapPool():
    """
    线程池，map分发线程任务
    """
    def __init__(self, pool_num):
        self.pool_num = pool_num

    def run(self, target, param_list):
        pool = ThreadPool(self.pool_num)
        pool.map(target, param_list)
        pool.close()
        pool.join()


class Producer():
    """
    生产者，向线程加入处理函数及对应的参数列表
    分为普通模式和队列模式
    """
    def __init__(self):
        self.queue = Queue.Queue()
        self.result_list = []

    def run(self, process_func, request_list):
        pool_num = len(request_list)
        map_pool = MapPool(pool_num=pool_num)
        map_pool.run(target=process_func, param_list=request_list)

    def run_with_queue(self, process_func, request_list):
        """
        if (process_func.__name__!= "wrapper"):
            raise BaseException("the producer run with queue must be decrorated by put_queue")
        """
        self.run(process_func, request_list)

    def put_queue(self, func):
        """
        放入队列的修饰器，当有run_with_queue方法时必须加上
        """

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            self.queue.put(result)
        return wrapper

    def get_queue_list(self):
        """
        取出队列里的内容，放入list中，返回
        :return:queue list
        """
        while not self.queue.empty():
            self.result_list.append(self.queue.get())
        return self.result_list
