"""
    Create by: FlyingBlade
    Create Time: 2018/7/26 16:02
"""


# 工作日/节假日客流对比
class Module(object):
    def __init__(self):
        from common.TempletLoader import TempletLoader
        self.__templete = TempletLoader('templets/module_workholi_cmp.txt')
        self.__city_dict = {'广州': ['机场南', '广州东站'], }
        self.__params = {}
        self.__data = {}

    def run(self, df, global_params=None):
        if global_params is None:
            global_params = {}
        df_suc = df[df.order_status == 5][['ticket_num', 'entry_date', 'entry_station', 'exit_station']]
        df_suc['weekday'] = df_suc.entry_date.map(lambda x: x.weekday())
        df_suc['hour'] = df_suc.entry_date.map(lambda x: x.hour)
        days = df_suc.entry_date.max() - df_suc.entry_date.min()
        days = days.round('d').days
        workday_seq = (df_suc[df_suc.weekday < 5].groupby('hour').ticket_num.sum().sort_index() / days).map(
            lambda x: round(x, 3))
        holiday_seq = (df_suc[df_suc.weekday >= 5].groupby('hour').ticket_num.sum().sort_index() / days).map(
            lambda x: round(x, 3))
        self.__params['workday_seq_maxhour'] = workday_seq.argmax()
        self.__params['workday_seq_maxfluency'] = int(workday_seq.max())
        self.__params['holiday_seq_maxhour'] = holiday_seq.argmax()
        self.__params['holiday_seq_maxfluency'] = int(holiday_seq.max())
        workday_seqs = {}
        holiday_seqs = {}
        for station in self.__city_dict[global_params.get('city', '广州')]:
            workday_seqs[station] = (df_suc[(df_suc.entry_station == station) & (df_suc.weekday < 5)].groupby(
                'hour').ticket_num.sum().sort_index() / days).map(lambda x: round(x, 3))
            holiday_seqs[station] = (df_suc[(df_suc.entry_station == station) & (df_suc.weekday >= 5)].groupby(
                'hour').ticket_num.sum().sort_index() / days).map(lambda x: round(x, 3))
        # 填数据
        self.__data['workday_full_seq'] = [workday_seq.index.tolist(), workday_seq.tolist()]
        self.__data['holiday_full_seq'] = [holiday_seq.index.tolist(), holiday_seq.tolist()]
        self.__data['stations'] = self.__city_dict[global_params.get('city', '广州')]
        self.__data['station_workday_seqs'] = {
        station: [workday_seqs[station].index.tolist(), workday_seqs[station].tolist()] for station in
        self.__data['stations']}
        self.__data['station_holiday_seqs'] = {
        station: [holiday_seqs[station].index.tolist(), holiday_seqs[station].tolist()] for station in
        self.__data['stations']}

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
        return json.dumps(self.__data, ensure_ascii=False)
        # return ''
