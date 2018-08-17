# import logging
# from flask import current_app
from info import redis_store
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
    redis_store.set('name','laowang')
    return "index22233"