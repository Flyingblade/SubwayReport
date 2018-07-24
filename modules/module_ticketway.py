# -*- coding: utf-8 -*-
"""
    @Time    : 2018/7/23 11:47
    @Author  : ZERO
    @FileName: module_ticketway.py
    @Software: PyCharm
    @Github    ：https://github.com/abcdddxy
"""

import pandas as pd


class Module(object):
    def __init__(self):
        from common.TempletLoader import TempletLoader
        self.__templete = TempletLoader('templets/module_ticketway.txt')
        self.__params = {}

    def run(self, df):
        # STATUS ==5 的是交易成功的
        # payment_type source
        payment_type_dict = {
            0: '支付宝', 1: '中移动', 2: '支付宝网上购票', 3: '微信支付', 4: '微信扫码支付', 5: '翼支付', 6: '支付宝网页支付', 7: '微信公众号支付',
            8: '首信易支付', 9: '中移动WAP支付', 10: '银联支付', 11: '银联支付', 12: '微信小程序支付'
        }
        source_dict = {
            1: '盘缠ios', 2: '盘缠android', 3: '插件ios', 4: '插件android', 5: 'h5公众号或扫码支付', 6: '非闪客蜂公众号', 7: '咖啡', 8: '长沙ios',
            9: '长沙android'
        }
        df_suc = df[df['order_status'] == 5]

        tmp = df_suc.groupby(['entry_station', 'exit_station']).ticket_num.sum().reset_index()
        starts = df_suc.groupby('entry_station').ticket_num.sum().sort_values(ascending=False)
        df_suc.payment_type = df_suc.payment_type.astype(int)
        df_suc.source = df_suc.source.astype(int)
        df_suc.payment_type = df_suc.payment_type.map(payment_type_dict)
        df_suc.source = df_suc.source.map(source_dict)
        df_suc = df_suc[df_suc.entry_station.isin(starts[:10].index.tolist())]
        total = df_suc.shape[0]

        type = df_suc.groupby(['payment_type']).ticket_num.count().sort_values(ascending=False)
        source = df_suc.groupby(['source']).ticket_num.count().sort_values(ascending=False)
        type = type / total
        source = source / total
        # print(type.head())
        # print(source.head())

        self.__params['M4_stations'] = starts[:10].index.tolist()
        self.__params['M4_top_methods'] = source.index
        self.__params['M4_top_source'] = type.index
        self.__params['M4_top_perc'] = source
        self.__params['M4_top_perc_source'] = type
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
