"""
    Create by: FlyingBlade
    Create Time: 2018/7/26 16:03
"""


# 上下班高峰期拥堵路段分析
class Module(object):
    def __init__(self):
        from common.TempletLoader import TempletLoader
        self.__templete = TempletLoader('templets/module_jamanalize.txt')
        self.__params = {}
        self.__data = {}
        self.name = "module_jamanalize"
        self.__time_period = [(7, 9), (17, 19)]  # 长度必须为2，代表早晚上班时段
    def run(self, df, global_params=None):
        import pickle as pk
        import pandas as pd
        import os
        if global_params is None:
            global_params = {}
        # 用最短路径作为预测
        city = global_params.get('city', '广州')
        if not os.path.exists('routes/%s_route.pk' % city):
            return
        routes = pk.load(open('routes/%s_route.pk' % city, 'rb'))
        # 生成(工作日、周末) x (上班时段、下班时段) 路径人数并排序
        df_suc = df[df.order_status == 5]
        df_suc['weekday'] = df_suc.entry_date.map(lambda x: x.weekday())
        df_suc['hour'] = df_suc.entry_date.map(lambda x: x.hour)
        morning = self.__time_period[0]
        evening = self.__time_period[1]
        df_workday_morning = df_suc[
            (df_suc.weekday < 5) & (df_suc.hour >= morning[0]) & (df_suc.hour <= morning[1])].groupby(
            ['entry_station', 'exit_station']).ticket_num.sum().reset_index().values
        df_workday_evening = df_suc[
            (df_suc.weekday < 5) & (df_suc.hour >= evening[0]) & (df_suc.hour <= evening[1])].groupby(
            ['entry_station', 'exit_station']).ticket_num.sum().reset_index().values
        df_holiday_morning = df_suc[
            (df_suc.weekday >= 5) & (df_suc.hour >= morning[0]) & (df_suc.hour <= morning[1])].groupby(
            ['entry_station', 'exit_station']).ticket_num.sum().reset_index().values
        df_holiday_evening = df_suc[
            (df_suc.weekday >= 5) & (df_suc.hour >= evening[0]) & (df_suc.hour <= evening[1])].groupby(
            ['entry_station', 'exit_station']).ticket_num.sum().reset_index().values
        error_counts = 0
        try:
            for d in ['workday', 'holiday']:
                for t in ['morning', 'evening']:
                    locals()['%s_%s_res' % (d, t)] = {}
                    for row in locals()['df_%s_%s' % (d, t)]:
                        if row[0] == row[1]:
                            continue
                        for path in routes[(row[0], row[1])]:
                            locals()['%s_%s_res' % (d, t)][path] = locals()['%s_%s_res' % (d, t)].get(path, 0) + row[2]
                    del locals()['df_%s_%s' % (d, t)]
                    tmp = locals()['%s_%s_res' % (d, t)]
                    locals()['%s_%s_res' % (d, t)] = pd.DataFrame(
                        [{'start': each[0], 'end': each[1], 'line':each[2],'fluency': tmp[each]} for each in tmp]).sort_values('fluency',ascending=False)
                    locals()['%s_%s_res'% (d, t)]['level'] = pd.cut(locals()['%s_%s_res'%(d, t)]['fluency'], 5, labels=False)
                    self.__params['%s_%s_jam_routes'% (d, t)] = '\n'.join([','.join(each) for each in locals()['%s_%s_res'% (d, t)][locals()['%s_%s_res'% (d, t)].level==4][['start','end','line','fluency']].astype(str).values])
                    del tmp
                    for jam_lv in range(0,5):
                        if jam_lv == 0:
                            self.__data['%s_%s_jam_routes'%(d, t)] = {}
                        self.__data['%s_%s_jam_routes' % (d, t)][jam_lv] = locals()['%s_%s_res'% (d, t)][locals()['%s_%s_res'% (d, t)].level==jam_lv][['start', 'end', 'level']].as_matrix().tolist()
            global_params['M7_AM_busy_routes'] = '、'.join('-'.join([str(x) for x in each[:2]]) for each in self.__data['workday_morning_jam_routes'][4][:3])
        except:
            error_counts += 1
        print('----Jam Analize Finished. %d error meet.'%error_counts)
        global_params['M7_AM_lv4_count'] = len(self.__data['workday_morning_jam_routes'][4])
        global_params['M7_AM_lv4_rate'] = '%.2f'%(global_params['M7_AM_lv4_count'] / len(routes) * 100)
        global_params['M7_PM_busy_routes'] = '、'.join('-'.join([str(x) for x in each[:2]]) for each in self.__data['workday_evening_jam_routes'][4][:3])
        global_params['M7_PM_lv4_count'] = len(self.__data['workday_evening_jam_routes'][4])
        global_params['M7_PM_lv4_rate'] = '%.2f'%(global_params['M7_PM_lv4_count'] / len(routes) * 100)


    def maketext(self, global_params=None):
        # 允许传入全局变量， 但局部变量的优先级更高
        if global_params and type(global_params) == dict:
            for param in global_params:
                if param not in self.__params:
                    self.__params[param] = global_params[param]
        # 如果有缺失的变量， 填空字符串
        for param in self.__templete.get_params():
            if param not in self.__params:
                self.__params[param] = ''
        # 返回format结果
        return self.__templete.format_templet(self.__params)

    def makedata(self):
        import json
        from common.MyEncoder import MyEncoder
        return json.dumps(dict(self.__data), ensure_ascii=False, cls=MyEncoder)
        # return ''