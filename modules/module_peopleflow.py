# -*- coding: utf-8 -*-
"""
    @Time    : 2018/7/20 10:08
    @Author  : ZERO
    @FileName: module_peopleflow.py
    @Software: PyCharm
    @Github    ：https://github.com/abcdddxy
"""
import pandas as pd


class Module(object):
    def __init__(self):
        from common.TempletLoader import TempletLoader
        self.__templete = TempletLoader('templets/module_peopleflow.txt')
        self.__params = {}

    def run(self, df):
        # STATUS ==5 的是交易成功的
        df_suc = df[df['ORDER_STATUS'] == 5]
        # df['time'] = pd.to_datetime(df['NOTI_TAKE_TICKET_RESULT_DATE'], format='%Y-%m-%d %H:%M:%S')
        df_suc['hour'] = df_suc['NOTI_TAKE_TICKET_RESULT_DATE'].apply(lambda x: x.hour)

        tmp = df_suc.groupby(['START_NAME', 'END_NAME']).SINGLE_TICKET_NUM.sum().reset_index()
        starts = tmp.groupby('START_NAME').SINGLE_TICKET_NUM.sum().sort_values(ascending=False)

        self.__params['M3_stations'] = starts[:3].index.tolist()
        self.__params['M3_station0_t1'] =
        self.__params['M3_station0_t2'] =
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
