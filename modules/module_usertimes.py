"""
    Create by: FlyingBlade
    Create Time: 2018/8/2 20:39
"""


# 用户使用次数统计
class Module(object):
    def __init__(self):
        from common.TempletLoader import TempletLoader
        self.__templete = TempletLoader('templets/module0.txt')
        self.__params = {}
        self.__data = {}
        self.name = "module_usertimes"

    def run(self, df, global_params=None):
        if global_params is None:
            global_params = {}
        user_counts = df[df.order_status == 5].groupby('owner_id').order_no.count().reset_index().rename(
            columns={'order_no': 'user_counts'})
        user_counts['user_counts_level'] = user_counts.user_counts.map(
            lambda x: '1次' if x == 1 else '2-5次' if x <= 5 else '6-20次' if x <= 20 else '20次以上')
        user_counts = user_counts.groupby('user_counts_level').owner_id.count().to_dict()
        # 填数据
        self.__data['levels'] = list(user_counts.keys())
        self.__data['user_times'] = user_counts
        counts_sum = sum(user_counts.values())
        self.__data['user_percent'] = {each:user_counts[each] / counts_sum for each in user_counts}


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