import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, config
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from redis import StrictRedis

from config import config

# 初始化数据库
# 在flask很多扩展里可以先初始化扩展的对象，再用init_app初始化


db = SQLAlchemy()
redis_store = None

def setup_log(config_name):
    """配置日志"""

    # 设置日志的记录等级
    logging.basicConfig(level=config[config_name].LOG_LEVEL)  # 调试debug级

    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)

    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')

    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)

    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

# create_app类似工厂方法
def create_app(config_name):
    # 配置日志并传入配置名字，以便能获取到指定配置的文件日志等级
    setup_log(config_name)
    # 创建flask对象
    app = Flask(__name__)

    # 从app加载配置
    app.config.from_object(config[config_name])

    db.init_app(app)

    # 初始化Redis对象
    global redis_store
    redis_store = StrictRedis(host=config[config_name].REDIS_HOST,port=config[config_name].REDIS_PORT,decode_responses=True)

    # 开启CSRF保护,只做服务器验证功能
    # 已经帮我们做了：从cookie中取出随机值，从表单中取出随机值，进行校验，并响应校验结果
    # 我们需要做：1.在页面加载的时候，往cookie中添加csrf_token,并且在表单中添加一个隐藏的csrf_token  2.因为没有使用表单，所以在ajax请求中带有csrf_token就行
    CSRFProtect(app)

    #设置session保存指定位置
    Session(app)

    @app.after_request
    def after_request(response):
        # 生成随机的csrf_token的值
        csrf_token = generate_csrf()
        # 设置一个cookie
        response.set_cookie("csrf_token",csrf_token)
        return response

    from flask import render_template, g
    from info.utils.set_filters import user_login_data
    @app.errorhandler(404)
    @user_login_data
    def page_not_found(_):
        user = g.user
        data = {"user_info": user.to_dict() if user else None}
        return render_template('news/404.html', data=data)
        return app



    # 注册蓝图
    from info.modules.index import index_blue
    app.register_blueprint(index_blue)

    from info.modules.passport import passport_blue
    app.register_blueprint(passport_blue)

    from info.utils.set_filters import set_filter
    app.add_template_filter(set_filter,"set_class")

    from info.modules.news import news_blue
    app.register_blueprint(news_blue)

    from info.modules.profile import profile_blue
    app.register_blueprint(profile_blue)

    return app