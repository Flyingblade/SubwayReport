# -*- coding: utf-8 -*-
"""
    @Time    : 2018/7/26 16:10
    @Author  : ZERO
    @FileName: module_details.py
    @Software: PyCharm
    @Github    ：https://github.com/abcdddxy
"""
import numpy as np
import pandas as pd
import json
import codecs
from datetime import date, timedelta, datetime


# 用户模式函数
def days(start, end):
    start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
    return (end - start).days


def user_months_and_count(df):
    df_sub = df[['owner_id', 'reg_month']]
    df_sub['count'] = 1
    df_sub = df_sub.groupby(['owner_id', 'reg_month'])['count'].count().reset_index()
    user_month_dict = dict()
    user_mcount_dict = dict()
    for item in df_sub[['owner_id', 'reg_month', 'count']].values:
        if item[0] not in user_month_dict.keys():
            user_month_dict[item[0]] = list()
            user_mcount_dict[item[0]] = list()
        user_month_dict[item[0]].append(item[1])
        user_mcount_dict[item[0]].append(item[2])
    return user_month_dict, user_mcount_dict


def user_ft_lt(df):
    df_sub = df[['owner_id', 'first_time', 'last_time']].drop_duplicates()
    user_ft_lt = dict()
    for item in df_sub[['owner_id', 'first_time', 'last_time']].values:
        user_ft_lt[item[0]] = (item[1], item[2])
    return user_ft_lt


def user_work_week_num(df):
    user_workdays = dict()
    user_weekdays = dict()
    user_work_num = dict()
    user_week_num = dict()
    for item in df[['owner_id', 'reg_date', 'dayofweek']].values:
        if item[0] not in user_workdays:
            user_workdays[item[0]] = set()
            user_weekdays[item[0]] = set()
        if item[2] < 5:
            user_workdays[item[0]].add(item[1][0:10])
            user_work_num[item[0]] = user_work_num.get(item[0], 0) + 1
        else:
            user_weekdays[item[0]].add(item[1][0:10])
            user_week_num[item[0]] = user_week_num.get(item[0], 0) + 1
    user_ww_dict = dict()
    for user_id in df['owner_id'].unique():
        work_num = user_work_num.get(user_id, 0)
        work_len = len(user_workdays[user_id])
        if work_len > 0:
            work_num = work_num / work_len
        week_num = user_week_num.get(user_id, 0)
        week_len = len(user_weekdays[user_id])
        if week_len > 0:
            week_num = week_num / week_len
        user_ww_dict[user_id] = (work_num, week_num)
    return user_ww_dict


def user_month_week_count(df):
    df_sub = df[['owner_id', 'reg_month', 'reg_day']]
    user_mw_dict = dict()
    tmp = dict()
    for item in df_sub[['owner_id', 'reg_month', 'reg_day']].values:
        if item[0] not in tmp.keys():
            tmp[item[0]] = dict()
        if item[1] not in tmp[item[0]].keys():
            tmp[item[0]][item[1]] = set()
        tmp[item[0]][item[1]].add((item[2] - 1) // 7)
    for uid in tmp.keys():
        user_weeks_per_month = []
        for m in tmp[uid].keys():
            user_weeks_per_month.append(len(tmp[uid][m]))
        user_mw_dict[uid] = np.mean(user_weeks_per_month)
    return user_mw_dict


def user_model(df, user_id, user_used_month, user_used_mcount, user_mw_dict, user_ft_lt_dict, user_ww_dict):
    # 是不是周末型
    workday_num, weekday_num = user_ww_dict[user_id]
    if (workday_num - weekday_num) >= 1:
        work_or_weekend = 'work'
    elif (workday_num - weekday_num) <= -1:
        work_or_weekend = 'weekend'
    else:
        work_or_weekend = 'all'

    today = df.reg_date.min()
    user_ft, user_lt = user_ft_lt_dict[user_id]
    user_used_days = days(user_ft, user_lt)
    user_ft_days = days(user_ft, today)  # 新用户距4.29今多少天

    user_days_per_month = np.mean(user_used_mcount[user_id])  # 每月使用天数
    user_weeks_per_month = user_mw_dict[user_id]

    if user_ft_days >= 30:  # 一个月前的新用户
        if user_used_days <= 30:  # 一段时间不再使用
            return 7
        elif (user_ft_days <= 90) or (len(user_used_month[user_id]) >= 3):  # 稳定型 (3个月内的新用户 或者 使用月数 >=3 的用户)
            if user_days_per_month > 10 or user_weeks_per_month > 2:  # 高频
                if work_or_weekend == 'work':
                    return 1
                elif work_or_weekend == 'weekend':
                    return 2
                else:
                    return 3
            else:  # 低频
                if work_or_weekend == 'work':
                    return 4
                elif work_or_weekend == 'weekend':
                    return 5
                else:
                    return 6
        else:  # 突发性
            if work_or_weekend == 'work':
                return 8
            elif work_or_weekend == 'weekend':
                return 9
            else:
                return 10
    else:  # 一个月内的新用户
        if work_or_weekend == 'work':
            return 11
        elif work_or_weekend == 'weekend':
            return 12
        else:
            return 13

        def month_diff(first, last='2018-04'):
            fy = int(first[0:4])
            fm = int(first[5:7])
            ly = int(last[0:4])
            lm = int(last[5:7])
            return (ly - fy - 1) * 12 + lm + 13 - fm

        def next_month(cur):
            cur_year = int(cur[0:4])
            cur_month = int(cur[5:7])
            next_year = cur_year
            next_month = cur_month + 1
            if cur_month == 12:
                next_month = 1
                next_year = cur_year + 1
            ans = str(next_year) + '-'
            if next_month < 10:
                ans += '0'
            ans += str(next_month)
            return ans

        def has_used_in_all_next_months(used_months, first_month, month_num):
            has = True
            months = []
            cur_month = next_month(first_month)
            for i in range(month_num):
                months.append(cur_month)
                cur_month = next_month(cur_month)
            for mon in months:
                if mon not in used_months:
                    has = False
                    break
            return has

        def has_used_in_one_next_months(used_months, first_month, month_num):
            has = False
            months = []
            cur_month = next_month(first_month)
            for i in range(month_num):
                months.append(cur_month)
                cur_month = next_month(cur_month)
            for mon in months:
                if mon in used_months:
                    has = True
            return has

        def used_next_month_count(df, fm, mons, func):
            df_sub = df[(df['first_month'] == fm)]
            df_sub['count'] = 1
            df_sub = df_sub.groupby(['owner_id', 'reg_month'])['count'].count().reset_index()
            single_user_month_dict = dict()
            for item in df_sub[['owner_id', 'reg_month']].values:
                if item[0] not in single_user_month_dict.keys():
                    single_user_month_dict[item[0]] = list()
                single_user_month_dict[item[0]].append(item[1])
            count = 0
            for user_id in df_sub['owner_id'].unique():
                used_month = single_user_month_dict[user_id]
                if func(used_month, fm, mons):
                    count += 1
            print('%s\t%s' % (count, df_sub['owner_id'].unique().shape[0]))


# 打印每天新增用户数量
def day_add_num_print(df):
    first = datetime.strptime(df['first_time'].min()[0:10], '%Y-%m-%d')
    last = datetime.strptime(df['first_time'].max()[0:10], '%Y-%m-%d')
    today = first
    while today <= last:
        tom = today + timedelta(days=(1))
        tmp = df[(today.strftime('%Y-%m-%d') < df['first_time']) & (df['first_time'] < tom.strftime('%Y-%m-%d'))]
        print('%s\t%s' % (today.strftime('%Y-%m-%d'), tmp['owner_id'].unique().shape[0]))
        today = tom


# 用户计数
def user_count_num(df, left, right=None):
    user_count = df.groupby('owner_id')['reg_date'].count().reset_index()
    user_count.rename(columns={'reg_date': 'count'}, inplace=True)
    if right is not None:
        tmp = user_count[(left <= user_count['count']) & (user_count['count'] <= right)]
        print('%s-%s\t%s' % (left, right, tmp.shape[0]))
    else:
        tmp = user_count[left <= user_count['count']]
        print('%s->\t%s' % (left, tmp.shape[0]))


def user_count_ratio(df, left, right=None):
    user_count = df.groupby('owner_id')['reg_date'].count().reset_index()
    user_count.rename(columns={'reg_date': 'count'}, inplace=True)
    if right is not None:
        tmp = user_count[(left <= user_count['count']) & (user_count['count'] <= right)]
        print('%s-%s\t%.2f' % (left, right, (tmp.shape[0] / user_count.shape[0]) * 100))
    else:
        tmp = user_count[left <= user_count['count']]
        print('%s->\t%.2f' % (left, (tmp.shape[0] / user_count.shape[0]) * 100))


def longest_continue_days(days):
    n = len(days)
    if n < 2:
        return n
    cur = 1
    ans = 1
    r = 1
    while r < n:
        if days[r] - days[r - 1] == 1:
            cur += 1
            ans = max(ans, cur)
        else:
            cur = 1
        r += 1
    return ans


def longest_used_days(df):
    df['count'] = 1
    df_sub = df.groupby(['owner_id', 'day_interval'])['count'].count().reset_index()
    user_used_days = dict()
    for item in df_sub[['owner_id', 'day_interval']].values:
        if item[0] not in user_used_days.keys():
            user_used_days[item[0]] = set()
        user_used_days[item[0]].add(item[1])
    for k in user_used_days.keys():
        user_used_days[k] = sorted(list(user_used_days[k]))
    user_continue_day_count = dict()
    for k in user_used_days.keys():
        user_continue_day_count[k] = longest_continue_days(user_used_days[k])
    return user_used_days, user_continue_day_count


def day_ratio(df, mi, ma, column):
    tmp = df[(mi <= df[column]) & (df[column] <= ma)]
    # print('%s-%s\t%.2f' % (mi, ma, (tmp['num'].sum() / user_num) * 100))
    return tmp['num'].sum()


def used_month_count(df):
    tmp = df[['owner_id', 'reg_month']].drop_duplicates()
    mon_count = tmp.groupby('owner_id')['reg_month'].count().reset_index()
    mon_count.rename(columns={'reg_month': 'mon_count'}, inplace=True)
    return mon_count


def month_diff(first, last=datetime.now().strftime('%Y-%m-%d')):
    fy = int(first[0:4])
    fm = int(first[5:7])
    ly = int(last[0:4])
    lm = int(last[5:7])
    return (ly - fy - 1) * 12 + lm + 13 - fm


def next_month(cur):
    cur_year = int(cur[0:4])
    cur_month = int(cur[5:7])
    next_year = cur_year
    next_month = cur_month + 1
    if cur_month == 12:
        next_month = 1
        next_year = cur_year + 1
    ans = str(next_year) + '-'
    if next_month < 10:
        ans += '0'
    ans += str(next_month)
    return ans


def has_used_in_all_next_months(used_months, first_month, month_num):
    has = True
    months = []
    cur_month = next_month(first_month)
    for i in range(month_num):
        months.append(cur_month)
        cur_month = next_month(cur_month)
    for mon in months:
        if mon not in used_months:
            has = False
            break
    return has


def has_used_in_one_next_months(used_months, first_month, month_num):
    has = False
    months = []
    cur_month = next_month(first_month)
    for i in range(month_num):
        months.append(cur_month)
        cur_month = next_month(cur_month)
    for mon in months:
        if mon in used_months:
            has = True
    return has


def used_next_month_count(df, fm, mons, func):
    df_sub = df[(df['first_month'] == fm)]
    df_sub['count'] = 1
    df_sub = df_sub.groupby(['owner_id', 'reg_month'])['count'].count().reset_index()
    single_user_month_dict = dict()
    for item in df_sub[['owner_id', 'reg_month']].values:
        if item[0] not in single_user_month_dict.keys():
            single_user_month_dict[item[0]] = list()
        single_user_month_dict[item[0]].append(item[1])
    count = 0
    for user_id in df_sub['owner_id'].unique():
        used_month = single_user_month_dict[user_id]
        if func(used_month, fm, mons):
            count += 1
    return count, df_sub['owner_id'].unique().shape[0]


def user_model_count(df):
    mc_list = []
    mc_ratio_list = []
    count = df.shape[0]
    for i in range(13):
        i = i + 1
        mc = df[df["model"] == i].shape[0]
        mc_list.append(mc)
        mc_ratio_list.append(mc / count)
    return mc_list, mc_ratio_list


class Module(object):
    def __init__(self):
        from common.TempletLoader import TempletLoader
        self.__templete = TempletLoader('templets/module_details.txt')
        self.__params = {}

    def run(self, df):
        # STATUS ==5 的是交易成功的
        df_suc = df[df['order_status'] == 5].copy()
        df_suc['datetime'] = pd.to_datetime(df_suc['reg_date'], format='%Y-%m-%d %H:%M:%S')
        df_suc['year'] = df_suc['reg_date'].map(lambda x: x.year)
        df_suc['month'] = df_suc['reg_date'].map(lambda x: x.month)
        df_suc['day'] = df_suc['reg_date'].map(lambda x: x.day)
        df_suc['hour'] = df_suc['reg_date'].map(lambda x: x.hour)
        df_suc['reg_date'] = df_suc['reg_date'].astype(str)
        df_suc['reg_month'] = df_suc['reg_date'].map(lambda x: x[0:7])
        df_suc['reg_day'] = df_suc['reg_date'].map(lambda x: int(x[8:10]))
        df_suc['dayofweek'] = df_suc['datetime'].apply(lambda x: x.dayofweek)

        single_ft = df_suc.groupby(['owner_id'])['reg_date'].min().reset_index()
        single_ft = single_ft.rename(index=str, columns={'reg_date': 'first_time'})
        df_suc = df_suc.merge(single_ft, on=['owner_id'], how='left')
        single_ft = df_suc.groupby('owner_id')['reg_date'].max().reset_index()
        single_ft = single_ft.rename(index=str, columns={'reg_date': 'last_time'})
        df_suc = df_suc.merge(single_ft, on=['owner_id'], how='left')

        df_suc['first_month'] = df_suc['first_time'].map(lambda x: x[0:7])
        df_suc['first_date_obj'] = df_suc['first_time'].map(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date())
        df_suc['reg_date_obj'] = df_suc['reg_date'].map(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S').date())
        df_suc['tmp'] = df_suc['reg_date_obj'] - df_suc['first_date_obj']
        df_suc['day_interval'] = df_suc['tmp'].map(lambda x: x.days)
        df_suc.drop(['first_date_obj', 'reg_date_obj', 'tmp'], axis=1, inplace=True)

        params = {}
        params['D_new_cont_month_fm'] = {}

        mon_count = used_month_count(df_suc)
        fm = df_suc.reg_date.min()[0:7]
        if fm <= df_suc.reg_date.max()[0:7]:
            D_new_cont_month = []
            D_new_cont_month_people = []
            total_people = 0
            # print(next_month(fm))
            for i in range(month_diff(fm) - 1):
                D_new_cont_month.append(i + 1)
                people, total_people = used_next_month_count(df_suc, fm, i + 1, has_used_in_all_next_months)
                D_new_cont_month_people.append(people)
            D_new_cont_month_ratio = list(np.array(D_new_cont_month_people) / (total_people + 1))
            params['D_new_cont_month_fm'][fm] = dict(zip(D_new_cont_month, D_new_cont_month_ratio))
        # print(params)

        D_total_month = list(range(1, month_diff(fm)))
        tmp_df = df_suc.groupby(['owner_id']).reg_month.unique().reset_index()
        tmp_df['unique_month'] = tmp_df['reg_month'].apply(lambda x: len(x))
        D_total_month_people = tmp_df.groupby(['unique_month']).owner_id.count().reset_index().owner_id.tolist()
        D_total_month = D_total_month[:len(D_total_month_people)]
        D_total_month_ratio = list(np.array(D_total_month_people) / sum(D_total_month_people))

        # user_used_days_qr: 用户所有使用过的天次，第一次使用为第0天
        # user_continue_day_count_qr: 用户最长连续使用天数
        # 可以由 user_used_days_qr -> (用户最后一次使用距第一次使用相隔多少天；用户使用频率，即使用的天数/相隔的天数)
        user_used_days_qr, user_continue_day_count_qr = longest_used_days(df_suc[['owner_id', 'day_interval']])

        user_continue_day_count_num_qr = dict()  # 最长连续使用天数的用户数量
        for k in user_continue_day_count_qr.keys():
            v = user_continue_day_count_qr[k]
            user_continue_day_count_num_qr[v] = user_continue_day_count_num_qr.get(v, 0) + 1
        continue_day_count_df_qr = pd.DataFrame()
        count_list = []
        num_list = []
        for k in user_continue_day_count_num_qr.keys():
            count_list.append(k)
            num_list.append(user_continue_day_count_num_qr[k])
        continue_day_count_df_qr = continue_day_count_df_qr.from_dict(
            {'continue_day_count': count_list, 'num': num_list})

        D_cont_day_people = []
        D_cont_day_people.append(day_ratio(continue_day_count_df_qr, 1, 1, 'continue_day_count'))
        D_cont_day_people.append(day_ratio(continue_day_count_df_qr, 2, 3, 'continue_day_count'))
        D_cont_day_people.append(day_ratio(continue_day_count_df_qr, 4, 7, 'continue_day_count'))
        D_cont_day_people.append(day_ratio(continue_day_count_df_qr, 8, 20, 'continue_day_count'))
        D_cont_day_people.append(day_ratio(continue_day_count_df_qr, 21, 999, 'continue_day_count'))
        D_cont_day_ratio = list(np.array(D_cont_day_people) / len(df_suc.owner_id.unique()))

        user_day_count_num_qr = dict()  # 总使用天数的用户数量 （最后一次-第一次）
        for k in user_used_days_qr.keys():
            v = user_used_days_qr[k][-1] + 1
            user_day_count_num_qr[v] = user_day_count_num_qr.get(v, 0) + 1
        day_count_df_qr = pd.DataFrame()
        count_list = []
        num_list = []
        for k in user_day_count_num_qr.keys():
            count_list.append(k)
            num_list.append(user_day_count_num_qr[k])
        day_count_df_qr = day_count_df_qr.from_dict({'day_count': count_list, 'num': num_list})

        D_total_day_people = []
        D_total_day_people.append(day_ratio(day_count_df_qr, 1, 1, 'day_count'))
        D_total_day_people.append(day_ratio(day_count_df_qr, 2, 5, 'day_count'))
        D_total_day_people.append(day_ratio(day_count_df_qr, 6, 20, 'day_count'))
        D_total_day_people.append(day_ratio(day_count_df_qr, 21, 30, 'day_count'))
        D_total_day_people.append(day_ratio(day_count_df_qr, 31, 60, 'day_count'))
        D_total_day_people.append(day_ratio(day_count_df_qr, 61, 90, 'day_count'))
        D_total_day_people.append(day_ratio(day_count_df_qr, 91, 120, 'day_count'))
        D_total_day_people.append(day_ratio(day_count_df_qr, 120, 999, 'day_count'))
        D_total_day_ratio = list(np.array(D_total_day_people) / len(df_suc.owner_id.unique()))

        user_ratio_num_qr = {10: 0, 20: 0, 30: 0, 40: 0, 50: 0, 60: 0, 70: 0, 80: 0, 90: 0, 100: 0, 101: 0}
        for k in user_used_days_qr.keys():
            n = len(user_used_days_qr[k])
            last_day = user_used_days_qr[k][-1] + 1
            ratio = n / last_day
            if ratio <= 0.1:
                user_ratio_num_qr[10] = user_ratio_num_qr[10] + 1
            elif ratio <= 0.2:
                user_ratio_num_qr[20] = user_ratio_num_qr[20] + 1
            elif ratio <= 0.3:
                user_ratio_num_qr[30] = user_ratio_num_qr[30] + 1
            elif ratio <= 0.4:
                user_ratio_num_qr[40] = user_ratio_num_qr[40] + 1
            elif ratio <= 0.5:
                user_ratio_num_qr[50] = user_ratio_num_qr[50] + 1
            elif ratio <= 0.6:
                user_ratio_num_qr[60] = user_ratio_num_qr[60] + 1
            elif ratio <= 0.7:
                user_ratio_num_qr[70] = user_ratio_num_qr[70] + 1
            elif ratio <= 0.8:
                user_ratio_num_qr[80] = user_ratio_num_qr[80] + 1
            elif ratio <= 0.9:
                user_ratio_num_qr[90] = user_ratio_num_qr[90] + 1
            elif n > 1:
                user_ratio_num_qr[100] = user_ratio_num_qr[100] + 1
            else:
                user_ratio_num_qr[101] = user_ratio_num_qr[101] + 1
        tmp_list = list(user_ratio_num_qr.values())
        D_user_ratio_people = [tmp_list[-1]] + tmp_list[:-1]
        D_user_ratio_ratio = list(np.array(D_user_ratio_people) / len(df_suc.owner_id.unique()))

        user_used_month, user_used_mcount = user_months_and_count(df_suc)
        user_mw_dict = user_month_week_count(df_suc)
        user_ft_lt_dict = user_ft_lt(df_suc)
        user_ww_dict = user_work_week_num(df_suc)
        u_ids = []
        u_mds = []
        for user_id in df_suc['owner_id'].unique():
            u_ids.append(user_id)
            u_mds.append(user_model(df_suc, user_id, user_used_month, user_used_mcount, user_mw_dict, user_ft_lt_dict,
                                    user_ww_dict))
        user_model_df = pd.DataFrame()
        user_model_df = user_model_df.from_dict({'owner_id': u_ids, "model": u_mds})
        D_model_people, D_model_ratio = user_model_count(user_model_df)

        self.__params['D_new_cont_month'] = D_new_cont_month
        self.__params['D_new_cont_month_people'] = D_new_cont_month_people
        self.__params['D_new_cont_month_ratio'] = D_new_cont_month_ratio
        self.__params['D_total_month'] = D_total_month
        self.__params['D_total_month_people'] = D_total_month_people
        self.__params['D_total_month_ratio'] = D_total_month_ratio
        self.__params['D_cont_day'] = ['连续使用1天', '连续使用2~3天', '连续使用4~7天', '连续使用8~20天', '连续使用21天以上']
        self.__params['D_cont_day_people'] = D_cont_day_people
        self.__params['D_cont_day_ratio'] = D_cont_day_ratio
        self.__params['D_total_day'] = ['总使用1天', '总使用2~5天', '总使用6~20天', '总使用21~30天', '总使用31~60天', '总使用61~90天',
                                        '总使用91~120天', '总使用121天以上']
        self.__params['D_total_day_people'] = D_total_day_people
        self.__params['D_total_day_ratio'] = D_total_day_ratio
        self.__params['D_user_pre'] = ['只使用1次', '0~0.1', '0.1~0.2', '0.2~0.3', '0.3~0.4', '0.4~0.5', '0.5~0.6', '0.6~0.7',
                                       '0.7~0.8', '0.8~0.9', '0.9~1']
        self.__params['D_user_pre_people'] = D_user_ratio_people
        self.__params['D_user_pre_ratio'] = D_user_ratio_ratio
        self.__params['D_model'] = ['稳定高频周末型', '稳定高频工作型', '稳定高频常用型', '稳定低频周末型', '稳定低频工作型', '稳定低频常用型', '一段时间之后不用型',
                                    '突发周末型', '突发工作型', '突发常用型', '本月新用户周末型', '本月新用户工作型', '本月新用户常用型']
        self.__params['D_model_people'] = D_model_people
        self.__params['D_model_ratio'] = D_model_ratio
        # print(self.__params)

        for k, v in self.__params.items():
            if 'people' not in k and 'ratio' not in k:
                params[k] = {}
                for i, vv in enumerate(v):
                    params[k][vv] = self.__params[k + '_ratio'][i]
            params['D_model_people'] = dict(zip(self.__params['D_model'], self.__params['D_model_people']))
        with codecs.open('./json/module_details.json', 'a', 'utf-8') as outf:
            json.dump(params, outf, ensure_ascii=False)

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
