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
import json
import codecs


class Module(object):
    def __init__(self):
        from common.TempletLoader import TempletLoader
        self.__templete = TempletLoader('templets/module_hotstation.txt')
        self.__params = {}
        self.name = "module_hotstation"

    def run(self, df, global_params=None):
        if global_params is None:
            global_params = {}
        # STATUS ==5 的是交易成功的
        df_suc = df[df['order_status'] == 5].copy()
        df_suc['entry_date'] = df_suc['entry_date'].astype(str)
        df_suc['date'] = df_suc['entry_date'].apply(lambda x: x[0:10])
        # df_suc['time'] = pd.to_datetime(df_suc['entry_date'], format='%Y-%m-%d %H:%M:%S')

        tmp = df_suc.groupby(['entry_station', 'exit_station']).ticket_num.sum().reset_index()
        starts = tmp.groupby('entry_station').ticket_num.sum().sort_values(ascending=False)
        ends = tmp.groupby('exit_station').ticket_num.sum().sort_values(ascending=False)
        station = pd.DataFrame()
        station['st_name'] = list(set(list(df_suc['entry_station']) + list(df_suc['exit_station'])))
        starts = pd.DataFrame(starts)
        starts = starts.reset_index()
        ends = pd.DataFrame(ends)
        ends = ends.reset_index()
        station = station.rename(index=str, columns={'st_name': 'entry_station'})
        # print(station.head())
        station = station.merge(starts, on=['entry_station'], how='left')
        station = station.rename(index=str, columns={'entry_station': 'exit_station'})
        station = station.merge(ends, on=['exit_station'], how='left')
        station['total_ticket'] = station.ticket_num_x + station.ticket_num_y
        station = station.sort_values(by=['total_ticket'], ascending=False)
        # print(station.head())

        trend = df_suc.groupby(['entry_station', 'date']).ticket_num.sum().reset_index()
        # print(trend.head())

        routes_groupby = df_suc.groupby(['entry_station', 'exit_station']).ticket_num.sum().sort_values(ascending=False).index.tolist()[:10]

        routes = reduce(operator.add, routes_groupby)
        routes = sorted(dict(Counter(routes)).items(), key=lambda x: x[1], reverse=True)[:10]

        self.__params['M2_hotstations'] = station[station.total_ticket > station.total_ticket.mean()].exit_station.tolist()
        self.__params['M2_hotroutes'] = routes_groupby
        self.__params['M2_hotroutes_topstations'] = [route[0] for route in routes][:5]
        # print(self.__params)

        params = {}
        params['M2_hotstations'] = self.__params['M2_hotstations']
        params['M2_hotstations_ticketnum'] = station[station.total_ticket > station.total_ticket.mean()].total_ticket.tolist()
        params['M2_hotstations_trend1_time'] = trend[trend.entry_station == self.__params['M2_hotstations'][0]].date.tolist()
        params['M2_hotstations_trend1'] = trend[trend.entry_station == self.__params['M2_hotstations'][0]].ticket_num.tolist()
        params['M2_hotstations_trend2_time'] = trend[trend.entry_station == self.__params['M2_hotstations'][1]].date.tolist()
        params['M2_hotstations_trend2'] = trend[trend.entry_station == self.__params['M2_hotstations'][1]].ticket_num.tolist()
        params['M2_hotstations_trend3_time'] = trend[trend.entry_station == self.__params['M2_hotstations'][2]].date.tolist()
        params['M2_hotstations_trend3'] = trend[trend.entry_station == self.__params['M2_hotstations'][2]].ticket_num.tolist()
        params['M2_hotroutes'] = routes_groupby
        params['M2_hotroutes_ticketnum'] = df_suc.groupby(['entry_station', 'exit_station']).ticket_num.sum().sort_values(ascending=False).tolist()[
                                           :10]

        self.__data = params
        global_params['M2_hotstations'] = '、'.join(params['M2_hotstations'])
        for i in range(3): global_params['M2_top%d'%(i+1)] = params['M2_hotstations'][i]
        for i in range(3): global_params['M2_hotroutes'] = '、'.join('-'.join(each) for each in params['M2_hotroutes'][:2])
        global_params['M2_hotroutes_topstations'] = '、'.join(self.__params['M2_hotroutes_topstations'][:3])

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
