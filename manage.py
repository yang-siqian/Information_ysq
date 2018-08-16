from flask_session import Session
from flask_wtf import CSRFProtect
from redis import StrictRedis
from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy


class Config(object):
    """项目的配置"""
    DEBUG = True
    SECRET_KEY ='Kx5jPQ5OAsxkNhOd+byp+mcTpiTpo9hS/YzHj6XuiW2woldfk1J8l5vJqhRG3tzm'
    # 为数据库添加配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql416@127.0.0.1:3306/information_ysq"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 为Redis添加配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    # session保存配置
    SESSION_TYPE = "redis"
    # 开启session签名
    SESSION_USE_SIGNER = False
    # 指定session保存的redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    # 设置需要过期
    SESSION_PERMANENT = False
    # 设置过期时间2天
    PERMANENT_SESSION_LIFETIME = 86400*2


app = Flask(__name__)

# 从app加载配置
app.config.from_object(Config)

# 初始化数据库
db = SQLAlchemy(app)

# 初始化Redis对象
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

# 开启CSRF保护,只做服务器验证功能
CSRFProtect(app)

#设置session保存指定位置
Session(app)

@app.route("/")
def index():
    session['name'] = 'laowang'
    return "index22233"

if __name__ == '__main__':
    app.run()