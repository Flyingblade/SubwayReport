"""
    Create by: FlyingBlade
    Create Time: 2018/6/19 16:49
"""
import gc
import sys
from random import randint
from datetime import datetime
from common.ModuleLoader import ModuleLoader
from common.DataLoader import DataLoader

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
        modules = ModuleLoader(module_dir, sys.argv[4:]).get_modules()
        global_params = {'city': city, 'start_month': start_month, 'end_month': end_month, 'modules': sys.argv[4:]}
        # 生成文件名?
        today = datetime.now()
        filename = '%04d%02d%02d_%06d' % (today.year, today.month, today.day, randint(0, 999999))
        f_html = open('result/' + filename + '.html', 'w', encoding='utf-8')
        f_js = open('result/' + filename + '.json', 'w', encoding='utf-8')
        # 读数据
        loader = DataLoader(db_ip='10.109.247.63', db_port=3306, db_user='root', passwd='hadoop', city='广州',
                            start_time=start_month, end_time=end_month, debug=True)
        # 进行分析
        # for df in loader.re():
        df = loader.read_all()
        gc.collect()
        for module in modules:
            module.run(df)
            text = module.maketext(global_params=global_params)
            pic = module.makedata()
            f_html.write(text)
            f_js.write(pic)
        f_html.close()
        f_js.close()
        print('job finished. Save to result/' + filename + '.html/.json')
    else:
        print('args not enough.exit.')
