"""
    Create by: FlyingBlade
    Create Time: 2018/7/23 20:49
"""


# 进出站分析
class Module(object):
    def __init__(self):
        from common.TempletLoader import TempletLoader
        self.__templete = TempletLoader('templets/module_inout_analize.txt')
        self.__city_dict = {'广州': ['机场南', '广州东站'], }
        self.__params = {}

    def run(self, df, global_params=None):
        if global_params is None:
            global_params = {}
        df_suc = df[df.order_status == 5][['ticket_num', 'entry_date', 'entry_station', 'exit_station']]
        df_suc['weekday'] = df_suc.entry_date.map(lambda x: x.weekday())
        df_suc['date'] = df_suc.entry_date.map(lambda x: str(x)[:10])
        stations = self.__city_dict[global_params.get('city', '广州')]

        # 日进出站人数
        entry_day_nums = {}
        exit_day_nums = {}
        # 日进出站排名
        entry_ranks = {}
        exit_ranks = {}
        # 周末去向分布
        weekend_exits = {}
        for station in stations:
            # 日进出站人数
            entry_day_count = df_suc[df_suc.entry_station == station].groupby('date').ticket_num.sum().sort_index()
            exit_day_count = df_suc[df_suc.exit_station == station].groupby('date').ticket_num.sum().sort_index()
            # 日进出站排名
            entry_rank = df_suc[df_suc.entry_station == station].groupby('entry_station').ticket_num.sum().sort_values(
                ascending=False)
            exit_rank = df_suc[df_suc.exit_station == station].groupby('exit_station').ticket_num.sum().sort_values(
                ascending=False)

            # 各站点客流去向,放进字典
            entry_tmp = df_suc[df_suc.entry_station == station].groupby('exit_station').ticket_num.sum().sort_values(
                ascending=False)
            entry_day_nums[station] = entry_day_count
            exit_day_nums[station] = exit_day_count
            entry_ranks[station] = entry_rank
            exit_ranks[station] = exit_rank
            weekend_exits[station] = entry_tmp

        # 填参数
        self.__params['stations'] = stations
        self.__params['stations_all'] = '，'.join(stations)
        for i in range(len(stations)):
            self.__params['st_%d_wk_top3' % i] = '、'.join(weekend_exits[stations[i]].head(3).index.tolist())

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
