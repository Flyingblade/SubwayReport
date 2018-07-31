import pymysql
import datetime as dt
from pandas import read_sql, DataFrame


class DataLoader(object):
    def __init__(self, db_ip, db_user, passwd, city, start_time, end_time, db_port=3306, debug=True):
        '''
        init a DataLoader
        :param db_ip: String, IP address of mysql database
        :param db_port: String or Int, Port of mysql database. default 3306
        :param passwd: String, Password of mysql database
        :param city: String, City name
        :param start_time: String, %Y-%m format like '2017-01'
        :param end_time: String, %Y-%m format
        '''
        city_parser = {
            '天津': 'sttrade1200', '青岛': 'sttrade2600', '长沙': 'sttrade4100', '广州': 'sttrade',
            '北京': 'sttrade4402', '上海': 'sttrade4404', '郑州': 'sttrade4500', '珠海': 'sttrade5190',
            '南宁': 'sttrade5300', '贵阳': 'sttrade5500', '西安': 'sttrade7100'
        }
        if city not in city_parser:
            raise RuntimeError('city %s not supported.' % city)

        self.db_ip = db_ip
        self.db_user = db_user
        self.db_passwd = passwd
        self.db_port = int(db_port)
        self.db_name = city_parser[city]
        self.start_time = dt.datetime.strptime(start_time, '%Y-%m')
        self.current_time = self.start_time
        self.end_time = dt.datetime.strptime(end_time, '%Y-%m')
        self.debug = debug
        self.sql_single_tk = '''select USER_ID as user_id,
                  ACCOUNT_ID as account_id, 
                  PAY_ACCOUNT as owner_id,
                  PAYMENT_TYPE as payment_type,
                  finance.tr_order_thrid.SOURCE as source,
                  order_no, 
                  single_ticket_price as ticket_price,
                  actual_take_ticket_num as ticket_num,
                  entry_station_code,
                  exit_station_code,
                  order_status,
                  reg_date,
                  ticket_date as entry_date
                  from(
                        select ORDER_NO as order_no,
                               SINGEL_TICKET_PRICE as single_ticket_price,
                               ACTUAL_TAKE_TICKET_NUM as actual_take_ticket_num,
                               PICKUP_STATION_CODE as entry_station_code,
                               GETOFF_STATION_CODE as exit_station_code,
                               REG_DATE as reg_date,
                               ORDER_STATUS as order_status,
                               NOTI_TAKE_TICKET_RESULT_DATE as ticket_date
                        from sttrade.owner_order_single_ticket
                        where REG_DATE>=%s and REG_DATE<%s#ORDER_STATUS=5 and 
                  ) A
                  left join finance.tr_order_thrid
                  on A.order_no=finance.tr_order_thrid.EXT_ORDER_ID;'''

    def read_month(self):
        while self.current_time < self.end_time:
            # if self.current_time >= self.end_time:
            #     return
            conn = pymysql.connect(host=self.db_ip, user=self.db_user, password=self.db_passwd, database=self.db_name,
                                   port=self.db_port, charset='utf8')
            print('connect success')
            sql = self.sql_single_tk[:]

            if self.debug:
                sql = sql[:-1] + " LIMIT 100000;"
            if self.current_time.month < 12:
                next_month = dt.datetime(self.current_time.year, self.current_time.month + 1, 1)
            else:
                next_month = dt.datetime(self.current_time.year + 1, 1, 1)
            current_str = self.current_time.strftime("%Y-%m-%d")
            next_str = next_month.strftime("%Y-%m-%d")
            df = read_sql(sql, conn, params=(current_str, next_str))
            conn.close()
            sql = "SELECT STATION_CODE, STATION_NAME_ZH FROM station_code;"
            df_code = read_sql(sql, conn).drop_duplicates('STATION_CODE')
            df = df.merge(
                df_code.rename(columns={"STATION_CODE": "entry_station_code", "STATION_NAME_ZH": "entry_station"}),
                on="entry_station_code", how='left', copy=False)
            df = df.merge(
                df_code.rename(columns={"STATION_CODE": "exit_station_code", "STATION_NAME_ZH": "exit_station"}),
                on="exit_station_code", how='left', copy=False)
            self.current_time = next_month
            yield df

    # def read_month2(self):
    #     while self.current_time < self.end_time:
    #         # if self.current_time >= self.end_time:
    #         #     return
    #         conn = pymysql.connect(host=self.db_ip, user=self.db_user, password=self.db_passwd, database=self.db_name,
    #                                port=self.db_port, charset='utf8')
    #         print('connect success')
    #         sql = self.sql_single_tk[:]
    #
    #         if self.debug:
    #             sql = sql[:-1] + " LIMIT 100000;"
    #         if self.current_time.month < 12:
    #             next_month = dt.datetime(self.current_time.year, self.current_time.month + 1, 1)
    #         else:
    #             next_month = dt.datetime(self.current_time.year + 1, 1, 1)
    #         current_str = self.current_time.strftime("%Y-%m-%d")
    #         next_str = next_month.strftime("%Y-%m-%d")
    #
    #         cursor = conn.cursor(pymysql.cursors.DictCursor)
    #         cursor.execute(sql, (current_str, next_str))
    #         df = DataFrame(cursor.fetchall())
    #
    #         sql = "SELECT STATION_CODE, STATION_NAME_ZH FROM station_code;"
    #         df_code = read_sql(sql, conn).drop_duplicates('STATION_CODE')
    #         df = df.merge(
    #             df_code.rename(columns={"STATION_CODE": "PICKUP_STATION_CODE", "STATION_NAME_ZH": "entry_station"}),
    #             on="PICKUP_STATION_CODE", how='left', copy=False)
    #         df = df.merge(
    #             df_code.rename(columns={"STATION_CODE": "GETOFF_STATION_CODE", "STATION_NAME_ZH": "exit_station"}),
    #             on="GETOFF_STATION_CODE", how='left', copy=False)
    #         self.current_time = next_month
    #         yield df

    def read_all(self):
        conn = pymysql.connect(host=self.db_ip, user=self.db_user, password=self.db_passwd, database=self.db_name,
                               port=self.db_port, charset='utf8')
        print('connect success')
        sql = self.sql_single_tk[:]

        if self.debug:
            sql = sql[:-1] + " LIMIT 10000;"
        current_str = self.current_time.strftime("%Y-%m-%d")
        end_str = self.end_time.strftime("%Y-%m-%d")
        df = read_sql(sql, conn, params=(current_str, end_str))

        sql = "SELECT STATION_CODE, STATION_NAME_ZH FROM station_code;"
        df_code = read_sql(sql, conn).drop_duplicates('STATION_CODE')
        conn.close()
        df = df.merge(
            df_code.rename(columns={"STATION_CODE": "entry_station_code", "STATION_NAME_ZH": "entry_station"}),
            on="entry_station_code", how='left', copy=False)
        df = df.merge(df_code.rename(columns={"STATION_CODE": "exit_station_code", "STATION_NAME_ZH": "exit_station"}),
                      on="exit_station_code", how='left', copy=False)
        return df


if __name__ == '__main__':
    loader = DataLoader(db_ip='10.109.247.63', db_port=3306, db_user='root', passwd='hadoop', city='广州',
                        start_time='2017-02', end_time='2017-03', debug=True)
    import time
    import gc

    t_start = time.clock()
    for df in loader.read_month():
        gc.collect()
        t = time.clock()
        print('time cost:%.2f' % (t - t_start))
        t_start = t
        # print(df)
        print('shape:', df.shape, 'time min:', df.entry_date.min())
        input()
