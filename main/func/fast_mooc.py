#-*- coding: utf-8 -*-
import requests
import json
import re
from multiprocessing.dummy import Pool as ThreadPool
import Queue
import logging;log = logging.getLogger('fast_mooc')

"""
Python MOOC Class
"""

class Mooc:
    def __init__(self):
        log.info('init the Mooc class here')
        self.host = 'www.icourse163.org'
        self.url = ''
        self.suggest_search_url = ''
        self.full_search_url = ''
        self.file_url = ''
        self.info_url = ''
        self.token = ''
        self.text_url = '/course/richText.htm?contentId='
        self.send_headers = {
            'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
            'Host':'www.icourse163.org',
        }

    def request_data(self,tid):
        postdata = tid+self.token
        url="http://"+self.host+self.url
        response = requests.post(url, postdata, headers=self.send_headers)
        return response.json()

    def request_suggest_search(self,prefix):
        postdata = str(prefix)+ self.token
        url="http://"+self.host+self.suggest_search_url
        response = requests.post(url, postdata, headers=self.send_headers)
        return response.json()

    def request_full_search(self,keyword):
        postdata = str(keyword)+ self.token
        url="http://"+self.host+self.full_search_url
        response = requests.post(url, postdata, headers=self.send_headers)
        return response.json()


    def request_pdf(self,cid,t ='3',unitId=''):
        postdata = 'cid='+str(cid)+ '&t=' + t + '&unitId='+str(unitId)+self.token
        url="http://"+self.host+self.file_url
        r = requests.post(url, postdata, headers=self.send_headers)
        result_dict =  r.json()

        if result_dict['results'] is not None:
            textOrigUrl = result_dict['results']['learnInfo']['textOrigUrl']
        else:
            textOrigUrl =''
        return textOrigUrl

"""
很简单的一个获取富文本的例子
============================================================================
帐号使用的是网友提供的帐号  
"""
class Mooc_Login(Mooc):
    def login(self):
        username = '535036628@qq.com'
        password = 'aikechengp'
        login_url = 'http://www.icourse163.org/passport/reg/icourseLogin.do'
        login_data = urllib.urlencode({
            'returnUrl': 'aHR0cDovL3d3dy5pY291cnNlMTYzLm9yZy8=',
            'failUrl': 'aHR0cDovL3d3dy5pY291cnNlMTYzLm9yZy9tZW1iZXIvbG9naW4uaHRtP2VtYWlsRW5jb2RlZD1PVEl3T0RJd09UZzNRSEZ4TG1OdmJRPT0=',
            'savelogin': 'true',
            'oauthType': '',
                'username': username,
                'passwd': password
        })
        request = urllib2.Request(
            url=login_url,
            data=login_data,
            headers=self.send_headers
        )
        self.cookies = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookies))
        self.opener.open(request)

    def request_richtext(self,contend_id):
        request = urllib2.Request(
            url='http://www.icourse163.org/course/richText.htm?contentId='+str(contend_id),
            headers=self.send_headers
        )
        result = self.opener.open(request)
        html_result = result.read()
        return html_result

"""
多线程 map 实现批量获取PDF文档
============================================================================
生产者，消费者设计模式
"""

class Map_Pool():
    def __init__(self,pool_num):
        self.pool_num = pool_num
    def run(self,target,param_list):
        pool = ThreadPool(self.pool_num)
        pool.map(target, param_list)
        pool.close()
        pool.join()

class Producer():
    def __init__(self):
        self.queue =  Queue.Queue()

    def single_post_pdf(self,pdf_id_unit):
        for key in pdf_id_unit:
            result = mooc.request_pdf(cid=key,unitId=pdf_id_unit[key])
            file_dict = {}
            file_dict[key] = result
            self.queue.put(file_dict)

'''获取pdf的主程序'''
@time_count(3)
def get_pdf_list(course_id):
    producer = Producer()
    pdf_list,pdf_dict = [],{}
    try:
        result_list = get_course_by_id(course_id)
    expect:
        return {}
    #判断是否有结果
    if isinstance(result_list, dict) and result_list["status"]["code"] >= 0:
    #返回未处理过的Pdf id列表
        pdf_id_list = get_pdf_id_list(result_list,course_id)
        if len(pdf_id_list) > 0:
            pool_num = (len(pdf_id_list)+1)/2
            map_pool = Map_Pool(pool_num=pool_num)
            map_pool.run(target=producer.single_post_pdf,param_list=pdf_id_list)

        while not producer.queue.empty():
            pdf_list.append(producer.queue.get())

        for i in pdf_list:
            pdf_dict.update(i)
        
        return pdf_dict,result_list
    else:
        return {}

'''课程时间运算'''
import time
def is_couse_going(start_time,end_time):
    cur_time = int(time.time()*1000)
    if cur_time > end_time:
        return 0 #已经结束
    elif cur_time < start_time:
        return 2 #还没开始
    else:
        return 1 #正在进行



		