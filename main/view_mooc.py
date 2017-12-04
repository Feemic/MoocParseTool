# -*- coding:utf-8 -*-
import re
import datetime
from . import main
from app import db
import func.fast_mooc as fast_mooc
from ..models import Mooc
from .forms import MoocCoursesForm
from func.mail_class import send_error
from flask import render_template, flash, request, redirect, url_for

import logging;log = logging.getLogger('mooc')
from forms import DownloadCmdForm

course_state_string = ['还没开始', '正在进行', '已经结束']


def mooc_search(param):
    search_list = fast_mooc.search_course(param)
    if isinstance(search_list, dict):
        return render_template('mooc_search_show.html', search_list=search_list)
    else:
        log.info('find not result')
        flash(u"尝试搜索，找不到资源，请检查关键词是否正确或直接输入网址解析")
        return redirect(url_for('main.mooc_submit'))


def mooc_resolution(tid, save_flag=False):
    cmd_form = DownloadCmdForm()
    if cmd_form.validate_on_submit():
        tid = cmd_form.tid.data.strip()
        batch_cmd = fast_mooc.BatchVideoScript()
        cmd_content = batch_cmd.run(tid)
        fast_mooc.save_content_as_cmd(cmd_content, tid)
        return fast_mooc.response_mooc_file(tid)

    result_dict = fast_mooc.get_course_by_id(tid)
    if result_dict is None:
        return redirect(url_for('main.mooc_submit'))
    if len(result_dict):
        if save_flag:
            save_course_db(course_name, tid, course_id)
        course_info_dict = {}
        course_time_state = fast_mooc.course_state(startTime,endTime)
        course_info_dict['course_time_state'] = course_state_string[course_time_state]
        return render_template('mooc_show.html', result_dict=result_dict, course_id_dict=course_info_dict, form=cmd_form)

    else:
        return redirect(url_for('main.mooc_submit'))


@main.route('/mooc', methods=['GET', 'POST'])
def mooc_submit():
    most_search_list = fast_mooc.get_most_search()
    form = MoocCoursesForm()
    if form.validate_on_submit():
        param = form.coursesid.data.strip()
        log.info("the submit param is :" + form.coursesid.data)
        tid = fast_mooc.get_tid_by_param(param)
        # can not find the tid ,maybe it is search predix
        if tid.strip() == '':
            if 'http://' in param:
                flash(u"当前仅支持icourse163的课程，请检查网址或参数是否正确")
            else:
                return mooc_search(param)
        else:
            # find the tid
            return mooc_resolution(tid, save_flag=True)
    return render_template('mooc_home.html', form=form, search_list=most_search_list)


@main.route('/mooc/<string:tid>', methods=['GET', 'POST'])
def mooc_api(tid):
    log.info('mooc interface')
    return mooc_resolution(tid=tid, save_flag=False)


# PDF批量解析接口
@main.route('/mooc_pdf_batch/<string:tid>', methods=['GET', 'POST'])
def mooc_pdf_batch(tid):
    try:
        (pdf_dict, result_dict) = fast_mooc.get_pdf_list(tid)
        if not fast_mooc.is_course_end(result_dict):
            return redirect(url_for('main.mooc_submit'))
        if result_dict is None or pdf_dict is None:
            return redirect(url_for('main.mooc_submit'))
    except Exception, e:
        log.error(e)
        return redirect(url_for('main.mooc_submit'))

    return render_template('mooc_single_pdf.html', pdf_dict=pdf_dict, result_dict=result_dict)


@main.route('/mooc_rtext/<string:course_id>', methods=['GET', 'POST'])
def mooc_rtext(course_id):
    html_result = fast_mooc.get_rich_text(course_id)
    if '/code' in html_result:
        pattern = r'<code(.*?)/code>'
        code_content = re.search(pattern, html_result, re.S | re.M)
        if code_content is not None:
            code_html = handle_code(code_content)
            return render_template('Readme.html', md_html=code_html, title='代码自动纠正，若发生错误请联系管理员')
    return render_template('mooc_rtext_show.html', html_result=html_result)

def save_course_db(course_name, id, course_id):
    agent = str(request.headers.get('User-Agent'))
    pattern = "\((.*?)\)"
    value = re.findall(pattern, agent)
    value = value[0] if len(value) else ''
    dt_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    try:
        db.session.add(mooc_info)
        db.session.commit()
    except Exception, e:
        db.session.rollback()
        log.exception("the mooc info saved to mysql failed:" + repr(e))
        send_error(str(e))
