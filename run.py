"""
    Create by: FlyingBlade
    Create Time: 2018/6/19 16:49
"""
import gc
import os
import sys
import time
from random import randint
from datetime import datetime
from common.ModuleLoader import ModuleLoader
from common.DataLoader import DataLoader
import json
import pdfkit

module_list = ["module_details", "module_dataanalize", "module_hotstation", "module_inout_analize", "module_jamanalize",
               "module_newuseranalize", "module_peopleflow", "module_ticketrate", "module_ticketway", "module_userstay",
               "module_usertimes", "module_workholi_cmp"]

if __name__ == "__main__":
    # 模块的路径
    module_dir = 'modules'
    # 参数说明：
    # python run.py city start_year-month end_year-month module1 module2 ...
    print('input_params:', sys.argv)
    if len(sys.argv) > 3:
        city = sys.argv[1]
        start_month = sys.argv[2]
        end_month = sys.argv[3]
        if sys.argv[4] != 'all':
            modules = ModuleLoader(module_dir, sys.argv[4:]).get_modules()
        else:
            modules = ModuleLoader(module_dir, module_list).get_modules()
        # 基础json
        params = {}
        params['city'] = city
        params['start_month'] = start_month
        params['end_month'] = end_month
        params['datetime'] = time.strftime("%Y-%m-%d", time.localtime())
        params['modules'] = sys.argv[4:]
        global_params = {'city': city, 'start': start_month, 'end': end_month, 'datestart': start_month,
                         'dateend': end_month, 'starttime': start_month, 'endtime': end_month,
                         'date1': start_month, 'date2': end_month, 'modules': sys.argv[4:], 'type':'测试',
                         'Modules': '<br />'.join(sys.argv[4:])}
        # 生成目录名
        today = datetime.now()
        global_params['datetime'] = today.strftime("%Y-%m-%d %H:%M")
        global_params['date'] = today.strftime("%Y-%m-%d")
        filename = '%04d%02d%02d_%06d' % (today.year, today.month, today.day, randint(0, 999999))
        while os.path.exists('result/' + filename):
            filename = '%04d%02d%02d_%06d' % (today.year, today.month, today.day, randint(0, 999999))
        os.makedirs('result/' + filename)
        os.makedirs('result/' + filename + '/json')
        os.makedirs('result/' + filename + '/html')
        # 读数据
        loader = DataLoader(db_ip='10.109.247.63', db_port=3306, db_user='root', passwd='hadoop', city=city,
                            start_time=start_month, end_time=end_month, debug=False)
        with open('result/' + filename + '/json/module_basic.json', 'w', encoding='utf-8') as outf:
            json.dump(params, outf, ensure_ascii=False)

        # 进行分析
        df = loader.read_all()
        print('load data success.')
        gc.collect()
        # 站点编号信息
        global_params['M0_6'], global_params['M0_7'], global_params['M0_8'] = loader.get_station_info()
        for module in modules:
            module.run(df, global_params=global_params)
            text = module.maketext(global_params=global_params)
            data = module.makedata()
            with open('result/' + filename + '/json/' + module.name + '.json', 'w', encoding='utf-8') as f_json:
                f_json.write(data)
        # html填写:
        f_html = open('result/' + filename + '/html/index.html', 'w', encoding='utf-8')
        with open('repo/basic-repo.html','r', encoding='utf-8') as f:
            templete = f.read()
            for param in global_params:
                templete = templete.replace(r'{'+param+r'}', str(global_params[param]))
            f_html.write(templete)
        f_html.close()
        # 其他文件
        otherfiles = ['bootstrap.min.css', 'echarts.js', 'jquery-1.11.2.min.js', 'templatemo-style.css']
        for otherf in otherfiles:
            with open('repo/' + otherf, 'r', encoding='utf-8') as f1:
                with open('result/' + filename + '/html/' + otherf, 'w', encoding='utf-8') as f2:
                    f2.write(f1.read())
        # 生成pdf
        # config = pdfkit.configuration(wkhtmltopdf=r'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe')
        # pdfkit.from_file('result/'+ filename + '/html/index.html', 'result/' + filename + '/html/index.pdf', configuration=config)
        print('job finished. Save to result/' + filename)
    else:
        print('args not enough.exit.')
