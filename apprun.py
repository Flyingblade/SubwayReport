# -*- coding: utf-8 -*-
"""
    @Time    : 2018/8/6 10:15
    @Author  : ZERO
    @FileName: apprun.py
    @Software: PyCharm
    @Github    ：https://github.com/abcdddxy
"""

from flask import Flask
from flask import request
from flask import render_template
import json
import datetime
import os
from common.JobController import JobController
app = Flask(__name__, static_url_path='/result',static_folder='result')
# dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "html")

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("html/region.html")


@app.route('/submit', methods=['POST'])
def submit():
    req = request.form
    ret = {'city': req.get('city', None),
           'start': req.get('start', None),
           'end': req.get('end', None),
           'job': req.get('job', None),
           'type': req.get('type', None),
           'modules': req.get('modules', None)
           }
    for param in ret:
        if ret[param] == None:
            return json.dumps({'success':0,'message':'Wrong Parameters!'})
    if ret['city'] not in ['广州','青岛','南宁']:
        return json.dumps({'success': 0, 'message': 'Wrong City!'})
    if datetime.datetime.strptime(ret['start'],'%Y-%m') >= datetime.datetime.strptime(ret['end'],'%Y-%m'):
        return json.dumps({'success': 0, 'message': 'Wrong Start or End!'})
    if ret['job'] not in ['单程票']:
        return json.dumps({'success': 0, 'message': 'Job not supported now!'})
    if ret['type'] not in ['基础','用户']:
        return json.dumps({'success': 0, 'message': 'Report type not supported!'})
    module_dict = {
        # base
        0:'module_dataanalize',
        1:'module_inout_analize',
        2:'module_peopleflow',
        3:'module_ticketway',
        4:'module_ticketrate',
        5:'module_hotstation',
        6:'module_jamanalize',
        7:'module_workholi_cmp',
        # user
        8:'module_newuseranalize',
        9:'module_usertimes',
        10:'module_userstay',
        11:'module_details'
    }
    module_list = []
    for m in ret['modules'].strip().split('+'):
        if not m.isalnum() or int(m) < 0 or int(m) > 11:
            return json.dumps({'success': 0, 'message': 'Wrong modules!'})
        m_name = int(m)
        if (m_name < 8 and ret['type'] == '用户') or (m_name >= 8 and ret['type'] == '基础'):
            return json.dumps({'success': 0, 'message': 'Wrong modules!'})
        m_name = module_dict[m_name]
        module_list.append(m_name)
    # 运行分析代码
    # os.system("python "+"run.py "+ret['city']+" "+ret['start']+" "+ret['end']+" "+" ".join(module_list)+" &")
    return json.dumps({'success':1, 'message':'Job Submitted!'})

@app.route('/getjobs', methods=['GET'])
def getjobs():
    from common.MyEncoder import MyEncoder
    # 读数据库
    jobs = JobController.get_all_jobs()
    module_parser = {
        'module_dataanalize':'整体数据统计',
        'module_inout_analize':'进出站客流分析',
        'module_peopleflow':'客流高峰期分析',
        'module_ticketway':'购票方式分析',
        'module_ticketrate':'购票转化率分析',
        'module_hotstation':'热门站点线路分析',
        'module_jamanalize':'上下班高峰期拥堵路段分析',
        'module_workholi_cmp':'工作日/节假日客流对比分析',
        'module_newuseranalize':'新增用户统计分析',
        'module_usertimes':'用户使用次数统计',
        'module_userstay':'用户留存情况分析',
        'module_details':'用户使用详情分析',
        'all':'全部模块分析'
    }
    for job in jobs:
        modules = job['modules'].split(',')
        for i in range(len(modules)):
            if modules[i] in module_parser:
                modules[i] = module_parser[modules[i]]
        job['modules'] = modules
    # print(jobs)
    # 结构化返回
    return json.dumps(jobs, cls=MyEncoder, ensure_ascii=False)




#
# @app.route('/region', methods=['GET'])
# def region_form():
#     print('return success')
#     return app.send_static_file('region.html')
#
#
# @app.route('/region', methods=['POST'])
# def region():
#     print(request.form)
#     return request.form['city']
# 需要从request对象读取表单内容：
# if request.form['username'] == 'admin' and request.form['password'] == 'password':
#     return '<h3>Hello, admin!</h3>'
# return '<h3>Bad username or password.</h3>'


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
