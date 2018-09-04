# -*- coding: utf-8 -*-
"""
    @Time    : 2018/7/24 9:11
    @Author  : ZERO
    @FileName: module_ticketrate.py
    @Software: PyCharm
    @Github    ：https://github.com/abcdddxy
"""
import numpy as np
import codecs
import json


class Module(object):
    def __init__(self):
        from common.TempletLoader import TempletLoader
        self.__templete = TempletLoader('templets/module_ticketrate.txt')
        self.__params = {}
        self.name = ""

    def run(self, df, global_params=None):
        # STATUS ==5 的是交易成功的
        df['is_success'] = df['order_status'].apply(lambda x: 1 if x == 5 else 0)
        status = df.groupby(['is_success']).ticket_num.count()
        st_status = df.groupby(['entry_station']).apply(lambda df: np.mean(df['is_success'])).reset_index()
        st_status.columns = ['entry_station', 'rate']
        st = df.groupby(['entry_station'], as_index=False).ticket_num.count()
        st_status = st_status.merge(st, on=['entry_station'], how='left')
        st_status['success_ticket'] = st_status['ticket_num'] * st_status['rate']
        st_status['success_ticket'] = st_status['success_ticket'].apply(lambda x: int(round(x)))
        st_status['fail_ticket'] = st_status['ticket_num'] - st_status['success_ticket']
        st_status = st_status.sort_values('rate', ascending=True)
        # print(st_status.head())

        self.__params['M5_total_rate'] = status[1] / status.sum()
        self.__params['M5_tail_stations'] = st_status.entry_station[:5].tolist()
        self.__params['M5_success_tk'] = st_status.success_ticket[:5].tolist()
        self.__params['M5_fail_tk'] = st_status.fail_ticket[:5].tolist()
        self.__params['M5_rate'] = st_status.rate[:5].tolist()
        # print(self.__params)

        params = {}
        params['M5_total_rate'] = self.__params['M5_total_rate']
        params['M5_tail_stations'] = self.__params['M5_tail_stations']
        params['M5_success_tk'] = self.__params['M5_success_tk']
        params['M5_fail_tk'] = self.__params['M5_fail_tk']
        params['M5_rate'] = self.__params['M5_rate']

        self.__data = params
        global_params['M5_total_rate'] = '%.2f'%(params['M5_total_rate']*100)
        global_params['M5_tail_stations'] = '、'.join(params['M5_tail_stations'][-3::-1])

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
        return json.dumps(self.__data, ensure_ascii=False)
