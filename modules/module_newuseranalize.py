"""
    Create by: FlyingBlade
    Create Time: 2018/7/26 19:54
"""


# 新增用户分析
class Module(object):
    def __init__(self):
        from common.TempletLoader import TempletLoader
        self.__templete = TempletLoader('templets/module0.txt')
        self.__params = {}
        self.__data = {}
        self.name = ""

    def run(self, df, global_params=None):
        if global_params is None:
            global_params = {}
        # 每个用户第一次使用作为新增
        user_reg_date = df.groupby('owner_id').reg_date.min().reset_index().rename(
            columns={'reg_date': 'user_reg_date'})
        # 计数， 每天新增人数
        user_reg_date['user_reg_day'] = user_reg_date.user_reg_date.map(lambda x:str(x)[:10])
        new_user_day_count = user_reg_date['user_reg_day'].value_counts().sort_index()
        # 填数据
        self.__data['new_user_day_count'] = [new_user_day_count.index.tolist(), new_user_day_count.tolist()]


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