# -*- coding: utf-8 -*-
"""
    @Time    : 2018/7/20 10:08
    @Author  : ZERO
    @FileName: module_peopleflow.py
    @Software: PyCharm
    @Github    ：https://github.com/abcdddxy
"""
import pandas as pd
import codecs
import json


class Module(object):
    def __init__(self):
        from common.TempletLoader import TempletLoader
        self.__templete = TempletLoader('templets/module_peopleflow.txt')
        self.__params = {}
        self.name = "module_peopleflow"

    def run(self, df, global_params=None):
        # STATUS ==5 的是交易成功的
        df_suc = df[df['order_status'] == 5].copy()
        df_suc['time'] = pd.to_datetime(df_suc['entry_date'], format='%Y-%m-%d %H:%M:%S')
        df_suc['hour'] = df_suc['time'].apply(lambda x: x.hour)

        tmp = df_suc.groupby(['entry_station', 'hour']).ticket_num.sum().reset_index()
        starts = df_suc.groupby('entry_station').ticket_num.sum().sort_values(ascending=False)
        hour = tmp[tmp.entry_station == starts.index[0]][tmp.ticket_num > (tmp[tmp.entry_station == starts.index[0]].ticket_num.mean()) * 1.3]
        # print(hour.head())

        self.__params['M3_stations'] = starts[:3].index.tolist()
        self.__params['M3_station0_t1'] = hour.hour.min()
        self.__params['M3_station0_t2'] = hour.hour.max()
        # print(self.__params)

        params = {}
        params['M3_stations'] = self.__params['M3_stations']
        params['M3_stations_trend1_time'] = tmp[tmp.entry_station == self.__params['M3_stations'][0]].hour.tolist()
        params['M3_stations_trend1'] = tmp[tmp.entry_station == self.__params['M3_stations'][0]].ticket_num.tolist()
        params['M3_stations_trend2_time'] = tmp[tmp.entry_station == self.__params['M3_stations'][1]].hour.tolist()
        params['M3_stations_trend2'] = tmp[tmp.entry_station == self.__params['M3_stations'][1]].ticket_num.tolist()
        params['M3_stations_trend3_time'] = tmp[tmp.entry_station == self.__params['M3_stations'][2]].hour.tolist()
        params['M3_stations_trend3'] = tmp[tmp.entry_station == self.__params['M3_stations'][2]].ticket_num.tolist()

        self.__data = params
        global_params['M3_station0_t1'] = self.__params['M3_station0_t1']
        global_params['M3_station0_t2'] = self.__params['M3_station0_t2']
        for i in range(3):
            global_params['M3_stations[%d]'%i] = self.__params['M3_stations'][i]

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
        from common.MyEncoder import MyEncoder
        return json.dumps(dict(self.__data), ensure_ascii=False, cls=MyEncoder)
