# -*- coding: utf-8 -*-
"""
    @Time    : 2018/7/19 11:08
    @Author  : ZERO
    @FileName: module_hotstation.py
    @Software: PyCharm
    @Github    ：https://github.com/abcdddxy
"""

from collections import Counter
import operator
from functools import reduce
import pandas as pd


class Module(object):
    def __init__(self):
        from common.TempletLoader import TempletLoader
        self.__templete = TempletLoader('templets/module_hotstation.txt')
        self.__params = {}

    def run(self, df):
        # STATUS ==5 的是交易成功的
        df_suc = df[df['ORDER_STATUS'] == 5]
        # df['time'] = pd.to_datetime(df['NOTI_TAKE_TICKET_RESULT_DATE'], format='%Y-%m-%d %H:%M:%S')
        df_suc['hour'] = df_suc['NOTI_TAKE_TICKET_RESULT_DATE'].apply(lambda x: x.hour)

        tmp = df_suc.groupby(['START_NAME', 'END_NAME']).SINGLE_TICKET_NUM.sum().reset_index()
        starts = tmp.groupby('START_NAME').SINGLE_TICKET_NUM.sum().sort_values(ascending=False)
        ends = tmp.groupby('END_NAME').SINGLE_TICKET_NUM.sum().sort_values(ascending=False)
        station = pd.DataFrame()
        station['st_name'] = list(set(list(df_suc['START_NAME']) + list(df_suc['END_NAME'])))
        starts = pd.DataFrame(starts)
        starts = starts.reset_index()
        ends = pd.DataFrame(ends)
        ends = ends.reset_index()
        station = station.rename(index=str, columns={'st_name': 'START_NAME'})
        # print(station.head())
        station = station.merge(starts, on=['START_NAME'], how='left')
        station = station.rename(index=str, columns={'START_NAME': 'END_NAME'})
        station = station.merge(ends, on=['END_NAME'], how='left')
        station['TOTAL_TICKET'] = station.SINGLE_TICKET_NUM_x + station.SINGLE_TICKET_NUM_y
        station = station.sort_values(by=['TOTAL_TICKET'], ascending=False)

        routes_groupby = df_suc.groupby(['START_NAME', 'END_NAME']).SINGLE_TICKET_NUM.sum().sort_values(
            ascending=False).index.tolist()[:10]
        routes = reduce(operator.add, routes_groupby)
        routes = sorted(dict(Counter(routes)).items(), key=lambda x: x[1], reverse=True)[:10]

        self.__params['M2_hotstations'] = station[station.TOTAL_TICKET > station.TOTAL_TICKET.mean()].END_NAME.tolist()
        self.__params['M2_hotroutes'] = routes_groupby
        self.__params['M2_hotroutes_topstations'] = [route[0] for route in routes][:5]
        # print(self.__params)

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
        return ''
