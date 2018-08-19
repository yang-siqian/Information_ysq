# import logging
# from flask import current_app
# from info import redis_store
from flask import render_template, current_app

from . import index_blue

@index_blue.route("/")
def index():
    # session['name'] = 'laowang'
    # 测试打印日志
    # logging.debug('测试debug')
    # logging.error('测试error')
    # logging.warning('测试warning')
    # logging.fatal('测试fatal')
    # current_app.logger.error('测试error')
    # redis_store.set('name','laowang')
    return render_template('news/index.html')

@index_blue.route("/favicon.ico")
def favicon():
    return current_app.send_static_file('news/favicon.ico')