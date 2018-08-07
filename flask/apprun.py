# -*- coding: utf-8 -*-
"""
    @Time    : 2018/8/6 10:15
    @Author  : ZERO
    @FileName: apprun.py
    @Software: PyCharm
    @Github    ：https://github.com/abcdddxy
"""

from flask import Flask
from flask import request

app = Flask(__name__, static_url_path='')


@app.route('/', methods=['GET', 'POST'])
def home():
    return '<h1>Home</h1>'


@app.route('/region', methods=['GET'])
def region_form():
    return app.send_static_file('region.html')


@app.route('/region', methods=['POST'])
def region():
    return request.form['city']
    # 需要从request对象读取表单内容：
    # if request.form['username'] == 'admin' and request.form['password'] == 'password':
    #     return '<h3>Hello, admin!</h3>'
    # return '<h3>Bad username or password.</h3>'


if __name__ == '__main__':
    app.run()
