# -*- coding: utf-8 -*-
"""
    @Time    : 2018/7/25 15:39
    @Author  : ZERO
    @FileName: module_userstay.py
    @Software: PyCharm
    @Github    ：https://github.com/abcdddxy
"""

import numpy as np
import pandas as pd
import json
import codecs
from datetime import date, timedelta, datetime


def day_actitve_num_print(df):
    us_date = []
    us_num = []
    first = datetime.strptime(df['reg_date'].min()[0:10], '%Y-%m-%d')
    last = datetime.strptime(df['reg_date'].max()[0:10], '%Y-%m-%d')
    # print(first, last)
    today = first
    while today <= last:
        tom = today + timedelta(days=(1))
        tmp = df[(today.strftime('%Y-%m-%d') < df['reg_date']) & (df['reg_date'] < tom.strftime('%Y-%m-%d'))]
        # print('%s\t%s' % (today.strftime('%Y-%m-%d'), tmp['owner_id'].unique().shape[0]))
        today = tom
        us_date.append(today.strftime('%Y-%m-%d'))
        us_num.append(tmp['owner_id'].unique().shape[0])
    return us_date, us_num


class Module(object):
    def __init__(self):
        from common.TempletLoader import TempletLoader
        self.__templete = TempletLoader('templets/module_userstay.txt')
        self.__params = {}
        self.name = ""

    def run(self, df, global_params=None):
        # STATUS ==5 的是交易成功的
        df_suc = df[df['order_status'] == 5].copy()
        single_ft = df_suc.groupby(['owner_id'])['reg_date'].min().reset_index()
        single_ft = single_ft.rename(index=str, columns={'reg_date': 'first_time'})
        df_suc = df_suc.merge(single_ft, on=['owner_id'], how='left')
        # print(df_suc[['owner_id', 'first_time', 'entry_date', 'reg_date']].head())
        df_suc['time'] = pd.to_datetime(df_suc['first_time'], format='%Y-%m-%d %H:%M:%S')
        df_suc['reg_date'] = df_suc['reg_date'].astype(str)
        df_suc['day'] = df_suc['time'].apply(lambda x: x.dayofweek)
        df_suc['is_weekend'] = df_suc['day'].apply(lambda x: 1 if x == 0 or x == 6 else 0)
        us_date, us_num = day_actitve_num_print(df_suc[df_suc['is_weekend'] == 1])

        self.__params['US_date'] = us_date
        self.__params['US_num'] = us_num
        # print(self.__params)

        params = {}
        params['US_date'] = self.__params['US_date']
        params['US_num'] = self.__params['US_num']

        self.__data = params

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