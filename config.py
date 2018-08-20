import logging
from redis import StrictRedis


class Config(object):
    """项目的配置"""
    # DEBUG = True
    SECRET_KEY ='Kx5jPQ5OAsxkNhOd+byp+mcTpiTpo9hS/YzHj6XuiW2woldfk1J8l5vJqhRG3tzm'
    # 为数据库添加配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql416@127.0.0.1:3306/information_ysq"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 自动提交
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

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

    # 设置日志等级
    LOG_LEVEL = logging.DEBUG


class DevelopmentConfig(Config):
    """开发环境下的配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境下的配置"""
    DEBUG = False
    LOG_LEVEL = logging.WARNING

class TestingConfig(Config):
    """单元测试环境下的配置"""
    DEBUG = True
    TESTING = True

config={
    "development":DevelopmentConfig,
    "production":ProductionConfig,
    "testing":TestingConfig
}