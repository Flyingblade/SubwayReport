"""
    Create by: FlyingBlade
    Create Time: 2018/7/23 20:30
"""


# 整体数据统计
class Module(object):
    def __init__(self):
        from common.TempletLoader import TempletLoader
        self.__templete = TempletLoader('templets/module_dataanalize.txt')
        self.__params = {}

    def run(self, df, global_params=None):
        if global_params is None:
            global_params = {}
        # 订单状态分布
        order_status = df.order_status.value_counts().to_dict()
        order_status_tk = df.groupby('order_status').ticket_num.sum().to_dict()
        print(order_status)
        # 订单总数
        order_nums = df.shape[0]
        # 出票订单数、购票但未取票订单数、失效订单数
        order_get_tk = order_status.get(5, 0)
        order_notpay = order_status.get(1, 0)
        order_pay_notuse = order_status.get(2, 0)
        order_canceled = order_status.get(3, 0) + order_status.get(6, 0) + order_status.get(7, 0)
        # 出票数、订单总票数
        tk_get_num = order_status_tk.get(5, 0)
        tk_get_sum = sum(order_status_tk.values())
        # 有过购票行为的站点数，站点编码数
        st_num = len(set(df.entry_station.unique()) | set(df.exit_station.unique()))
        st_code_num = len(set(df.entry_station_code.unique()) | set(df.exit_station_code.unique()))
        # 填充至变量中!
        # order_num, order_use_num, order_pay_not_use_num, order_fail_num, ticket_num, ticket_use_num
        self.__params['order_num'] = order_nums
        self.__params['order_use_num'] = order_get_tk
        self.__params['order_notpay'] = order_notpay
        self.__params['order_pay_not_use_num'] = order_pay_notuse
        self.__params['order_fail_num'] = order_canceled
        self.__params['ticket_num'] = tk_get_sum
        self.__params['ticket_use_num'] = tk_get_num

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
