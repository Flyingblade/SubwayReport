"""
    Create by: FlyingBlade
    Create Time: 2018/9/11 16:09
"""
import pymysql
class JobController(object):
    def __init__(self, job_code):
        self.__job_code = job_code

    def insert_db(self, city, start_month, end_month, modules, status=0):
        from common import config
        conn = pymysql.connect(host=config.db_ip, user=config.db_user, password=config.db_passwd, database="report",
                               port=config.db_port, charset='utf8')
        sql = "INSERT INTO job(job_id, city, start_month, end_month, modules, result_path, `status`) VALUES(%s, %s, %s, %s, %s, %s, %s)"
        cur = conn.cursor()
        try:
            cur.execute(sql, (
            self.__job_code, city, start_month, end_month, ','.join(modules), self.__job_code + '/html/index.htm', status))
        except:
            print('job_id',self.__job_code,'exists')
            return -1
        cur.close()
        conn.close()
        return 0

    def update_status(self, status=1):
        from common import config
        conn = pymysql.connect(host=config.db_ip, user=config.db_user, password=config.db_passwd, database="report",
                               port=config.db_port, charset='utf8')
        sql = "UPDATE job SET `status` = %s WHERE job_id = %s"
        cur = conn.cursor()
        effect_row = cur.execute(sql, (status, self.__job_code))
        if effect_row != 1:
            print('Attention:: effect row != 1')
            return -1
        cur.close()
        conn.close()
        return 0

    def get_job_info(self):
        from common import config
        conn = pymysql.connect(host=config.db_ip, user=config.db_user, password=config.db_passwd, database="report",
                               port=config.db_port, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
        sql = "SELECT * FROM job WHERE job_id = %s"
        cur = conn.cursor()
        effect_row = cur.execute(sql, (self.__job_code,))
        if effect_row >= 1:
            ret = cur.fetchone()
            ret['insert_time'] = ret['insert_time'].strftime('%Y-%m-%d %H:%M:%S')
            return ret
        else:
            print('can not find job', self.__job_code)
            return -1

    @staticmethod
    def get_all_jobs():
        from common import config
        conn = pymysql.connect(host=config.db_ip, user=config.db_user, password=config.db_passwd, database="report",
                               port=config.db_port, charset='utf8', cursorclass=pymysql.cursors.DictCursor)
        sql = "SELECT * FROM job"
        cur = conn.cursor()
        cur.execute(sql)
        ret = cur.fetchall()
        return ret

# if __name__ == '__main__':
#     j = JobController('20180911_369635')
#     j.insert_db('广州','2017-02','2017-03',['all'], 0)
#     # j.update_status(3)# 3 for test.
#     print(j.get_job_info())