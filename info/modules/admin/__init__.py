from flask import Blueprint

# 创建蓝图对象
admin_blue = Blueprint("admin",__name__)

from .views import *