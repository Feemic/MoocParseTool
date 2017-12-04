# -*- coding: utf-8 -*-
import requests
import urllib2
import urllib
import cookielib
import time
import numpy as np
import pandas as pd
import random
import re
import Queue
import logging;log = logging.getLogger('fast_mooc')
from app.plugins.pool_map import Producer
from flask import make_response, send_file
import codecs
import os


class Mooc:
    def __init__(self):
        pass

    def request_data(self, tid):
        postdata = 'tid=%s&mob-token=%s' % (tid, self.token)
        url = "http://%s%s" % (self.host, self.url)
        response = requests.post(url, postdata, headers=self.send_headers)
        return response.json()

    def request_suggest_search(self, prefix):
        postdata = 'prefix=%s&mob-token=%s' % (str(prefix), self.token)
        url = "http://%s%s" % (self.host, self.suggest_search_url)
        response = requests.post(url, postdata, headers=self.send_headers)
        return response.json()

    def request_full_search(self, keyword):
        postdata = 'psize=30&stats=0&p=1&keyword=%s&mob-token=%shighlight=true&orderBy=0&' % (str(keyword), self.token)
        url = "http://%s%s" % (self.host, self.full_search_url)
        response = requests.post(url, postdata, headers=self.send_headers)
        return response.json()

    def request_pdf(self, cid, t='3', unitid=''):
        postdata = 'cid=%s&t=%s&unitId=%s&mob-token=%s' % (str(cid), t, str(unitid), self.token)
        url = "http://" + self.host + self.file_url
        r = requests.post(url, postdata, headers=self.send_headers)
        result_dict = r.json()

        if result_dict['results'] is not None:
            text_orig_url = result_dict['results']['learnInfo']['textOrigUrl']
        else:
            text_orig_url = ''
        return text_orig_url


class MoocLogin(Mooc):
    def login(self):
        username = '535036628@qq.com'
        password = 'aikechengp'
        login_url = 'http://www.icourse163.org/passport/reg/icourseLogin.do'
        login_data = urllib.urlencode({
            'returnUrl': 'aHR0cDovL3d3dy5pY291cnNlMTYzLm9yZy8=',
            'failUrl': 'aHR0cDovL3d3dy5pY291cnNlMTYzLm9yZy9tZW1iZXIvbG9'
                       'naW4uaHRtP2VtYWlsRW5jb2RlZD1PVEl3T0RJd09UZzNRSEZ4TG1OdmJRPT0=',
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

    def request_richtext(self, contend_id):
        request = urllib2.Request(
            url='http://www.icourse163.org/course/richText.htm?contentId=' + str(contend_id),
            headers=self.send_headers
        )
        result = self.opener.open(request)
        html_result = result.read()
        return html_result


def get_tid_by_param(param):
    page_url = param
    if "icourse163" not in param:
        page_url = 'http://www.icourse163.org/course/' + str(param)
    elif 'learn' in page_url:
        page_url = page_url.replace('learn', 'course')
    try:
        response = requests.get(page_url)
        content = response.text
        couseid_pattern = re.compile('window.termDto.*?termId.*?"(\d+)', re.S)
        termid_result = re.findall(couseid_pattern, content)
        return termid_result[0] if termid_result is not None else ""
    except Exception, e:
        return ""


def get_course_by_id(id):
    try:
        result_json = mooc.request_data(id)
    except Exception, e:
        result_json = "find no result"
    return result_json


# 参数错误时进行搜索
def search_course_suggest(prefix):
    try:
        result_json = mooc.request_suggest_search(prefix=prefix)
    except Exception, e:
        log.error(str(e))
        result_json = "find no result"
    return result_json


# 新搜索函数
def search_course(prefix):
    try:
        result_json = mooc.request_full_search(keyword=prefix)
    except Exception, e:
        log.error(str(e))
        result_json = "find no result"
    return result_json


class BatchGetPdf(Producer):
    """
    批量获取PDF文档的消费者
    """
    def single_post_pdf(self, pdf_id_unit):
        """
        获取单个文档的线程处理
        :param pdf_id_unit:
        :return: 将结果加入队列
        """
        for key in pdf_id_unit:
            result = mooc.request_pdf(cid=key, unitid=pdf_id_unit[key])
            file_dict = {}
            file_dict[key] = result
            self.queue.put(file_dict)

    def get_all_pdf_list(self, course_id):
        """
        获取全部的PDF文档，加入列表，用线程池处理
        :param course_id:
        """
        pdf_list, pdf_dict = [], {}
        result_list = get_course_by_id(course_id)
        if isinstance(result_list, dict) and result_list.get('status', {}).get('code', -1) >= 0:
            pdf_id_list = get_pdf_id_list(result_list, course_id)
            if len(pdf_id_list) > 0:
                self.run_with_queue(self.single_post_pdf, pdf_id_list)

            pdf_list = self.get_queue_list()
            for i in pdf_list:
                pdf_dict.update(i)
            return pdf_dict, result_list
        else:
            return {}


'''批量获取pdf的主程序'''


def get_pdf_list(course_id):
    batch_get_pdf = BatchGetPdf()
    pdf_dict, result_list = batch_get_pdf.get_all_pdf_list(str(course_id))
    return pdf_dict, result_list


def get_rich_text(course_id):
    mooc_login.login()
    result = mooc_login.request_richtext(course_id)
    return result


'''课程时间运算'''
def course_state(start_time, end_time):
    cur_time = int(time.time() * 1000)
    if cur_time > end_time:
        return 2  # 已经结束
    elif cur_time < start_time:
        return 0  # 还没开始
    else:
        return 1  # 正在进行


def is_course_end(result_dict):
    try:
        start_time = result_dict['results']['termDto']['startTime']
        end_time = result_dict['results']['termDto']['endTime']
        course_time_state = course_state(start_time, end_time)
        if course_time_state == 2:
            return True
        else:
            return False
    except TypeError or KeyError:
        log.warning("a incorrect course id is in")
        return False


def response_mooc_file(tid):
    file_path = "/home/www/my_flask/myfiles/mooc_rename_%s.cmd" % (tid)
    response = make_response(send_file(file_path))
    response.headers["Content-Disposition"] = "attachment; filename=mooc_rename_%s.cmd;" % (tid)
    return response
