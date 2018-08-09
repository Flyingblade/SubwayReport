"""
    Create by: FlyingBlade
    Create Time: 2018/6/19 16:49
"""
import gc
import os
import sys
from random import randint
from datetime import datetime
from common.ModuleLoader import ModuleLoader
from common.DataLoader import DataLoader

module_list = ["module_inout_analize","module_hotstation","module_workholi_cmp","module_ticketway","module_ticketrate","module_jamanalize","module_peopleflow","module_dataanalize"]

if __name__ == "__main__":
    # 模块的路径
    module_dir = 'modules'
    # 参数说明：
    # python run.py city start_year-month end_year-month module1 module2 ...
    print('input_params:',sys.argv)
    if len(sys.argv) > 3:
        city = sys.argv[1]
        start_month = sys.argv[2]
        end_month = sys.argv[3]
        modules = ModuleLoader(module_dir, sys.argv[4:]).get_modules()
        global_params = {'city':city, 'start_month':start_month, 'end_month':end_month, 'modules':sys.argv[4:]}
        # 生成目录名
        today = datetime.now()
        filename = '%04d%02d%02d_%06d' % (today.year, today.month, today.day, randint(0, 999999))
        while os.path.exists('result/'+filename):
            filename = '%04d%02d%02d_%06d' % (today.year, today.month, today.day, randint(0, 999999))
        os.makedirs('result/'+filename)
        os.makedirs('result/'+filename+'/json')
        f_html = open('result/'+filename+'/index.html', 'w', encoding='utf-8')
        # 读数据
        loader = DataLoader(db_ip='10.109.247.63', db_port=3306, db_user='root', passwd='hadoop', city='广州',
                            start_time=start_month, end_time=end_month, debug=True)
        # 进行分析
        df = loader.read_all()
        gc.collect()
        for module in modules:
            module.run(df, global_params=global_params)
            text = module.maketext(global_params=global_params)
            data = module.makedata()
            f_html.write(text)
            with open('result/'+filename+'/json/'+module.name+'.json','w',encoding='utf-8') as f_json:
                f_json.write(data)
        f_html.close()

        print('job finished. Save to result/'+filename)
    else:
        print('args not enough.exit.')

