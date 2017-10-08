#-*- coding:utf-8 -*-
import re
import datetime
from . import main
from app import db
import func.fast_mooc
from ..models import MOOC
from .forms import MoocCoursesForm
from func.mail_class import Send_Error
from flask import render_template,flash,request,redirect, url_for
import logging;log = logging.getLogger('mooc')


def mooc_resolution(tid,save_flag=False):
    result_dict = func.fast_mooc.get_course_by_id(tid)
    if result_dict is None:
        flash(u'该课程还没开过课，请查找解析其它课程')
        return redirect(url_for('main.mooc_submit'))
    if len(result_dict) > 0:
        if save_flag:
            save_course_db(course_name, tid, course_id)
        course_time_state = func.fast_mooc.is_couse_going(start_time,end_time)
        course_info_dict['course_time_state'] = course_state_string[course_time_state]
        return render_template('mooc_show.html', result_dict=result_dict, course_id_dict=course_info_dict)

    else:
        flash(u"资源查找无结果或查找出错，请重试")
        return redirect(url_for('main.mooc_submit'))


@main.route('/mooc', methods=['GET','POST'])
def mooc_submit():
    most_search_list = func.fast_mooc.get_most_search()
    form = MoocCoursesForm()
    if  form.validate_on_submit():
        tid = func.fast_mooc.get_tid_by_param(param).strip()
        if tid:
		return mooc_resolution(tid,save_flag=True)
        else:            
	    if 'http://' in param:
                flash(u"当前仅支持icourse163的课程，请检查网址或参数是否正确")
            else:
                return mooc_search(param)
    return render_template('mooc.html',form=form,search_list = most_search_list)

@main.route('/mooc/<string:tid>', methods=['GET','POST'])
def mooc_api(tid):
    return mooc_resolution(tid =tid,save_flag=False

@main.route('/mooc_search/<string:tid>', methods=['GET','POST'])
def mooc_search_api(tid):
    return mooc_resolution(tid=tid,save_flag=True)

def save_course_db(course_name,id,course_id):
    agent = str(request.headers.get('User-Agent'))
    pattern= "\((.*?)\)"
    value = re.findall(pattern, agent)
    dt_now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    try:
        mooc_info = MOOC(id=id,course_id = str(course_id),name = course_name,datetime=dt_now,agent=value)
        db.session.add(mooc_info)
        db.session.commit()
    except Exception, e:
        db.session.rollback()
        log.exception("the mooc info saved to mysql failed:"+repr(e))
        Send_Error(str(e))
