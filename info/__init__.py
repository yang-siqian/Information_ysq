from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import Config

# 初始化数据库
db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)

    # 从app加载配置
    app.config.from_object(Config[config_name])

    db.init_app(app)

    # 初始化Redis对象
    redis_store = StrictRedis(host=Config[config_name].REDIS_HOST,port=Config[config_name].REDIS_PORT)

    # 开启CSRF保护,只做服务器验证功能
    CSRFProtect(app)

    #设置session保存指定位置
    Session(app)
