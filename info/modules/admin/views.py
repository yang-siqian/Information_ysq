from flask import render_template, request, current_app, g, redirect, url_for, session

from info.models import User
from info.modules.admin import admin_blue
from info.utils.set_filters import user_login_data


@admin_blue.route('/index')
@user_login_data
def admin_index():
    user = g.user
    return render_template('admin/index.html', user=user.to_dict())



@admin_blue.route('/login', methods=["GET", "POST"])
def admin_login():
    if request.method=="GET":
        # 去 session 中取指定的值
        user_id = session.get("user_id", None)
        is_admin = session.get("is_admin", False)
        # 如果用户id存在，并且是管理员，那么直接跳转管理后台主页
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))

        return render_template('admin/login.html')

    username = request.form.get("username")
    password = request.form.get("password")

    if not all([username, password]):
        return render_template('admin/login.html', errmsg="参数不足")

    try:
       user = User.query.filter(User.mobile == username).first()
    except Exception as e:
        current_app.logger.error(e)
        return render_template('admin/login.html', errmsg="数据查询失败")

    if not user:
        return render_template('admin/login.html', errmsg="用户不存在")

    if not user.check_passowrd(password):
        return render_template('admin/login.html', errmsg="密码错误")

    if not user.is_admin:
        return render_template('admin/login.html', errmsg="用户权限错误")

    session["user_id"] = user.id
    session["nick_name"] = user.nick_name
    session["mobile"] = user.mobile
    session["is_admin"] = True

    return redirect(url_for('admin.admin_index'))

