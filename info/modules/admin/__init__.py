from flask import Blueprint

# 创建蓝图对象
admin_blue = Blueprint("admin",__name__,url_prefix='/admin')

from .views import *


@admin_blue.before_request
def before_request():
    # 判断如果不是登录页面的请求
    if not request.url.endswith(url_for("admin.admin_login")):
        user_id = session.get("user_id")
        is_admin = session.get("is_admin", False)

        if not user_id or not is_admin:
            # 判断当前是否有用户登录，或者是否是管理员，如果不是，直接重定向到项目主页
            return redirect('/')