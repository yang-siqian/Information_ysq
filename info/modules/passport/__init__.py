from flask import Blueprint

# 创建蓝图对象
passport_blue = Blueprint("passport",__name__, url_prefix='/passport')

from .views import *