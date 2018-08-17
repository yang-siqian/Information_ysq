import logging
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from info import create_app,db


# 通过指定的配置名字创建对应配置的app
app = create_app('development')

manager = Manager(app)
# 将app与db关联
Migrate(app,db)
# 将迁移命令添加到manager中
manager.add_command('db',MigrateCommand)

@app.route("/")
def index():
    # session['name'] = 'laowang'
    # 测试打印日志
    logging.debug('测试debug')
    logging.error('测试error')
    logging.warning('测试warning')
    logging.fatal('测试fatal')
    return "index22233"

if __name__ == '__main__':
    manager.run()