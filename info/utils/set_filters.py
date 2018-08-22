# 定义过滤器
from flask import session, current_app, g

from info.models import User
import functools


def set_filter(index):
    if index == 1:
        return "first"
    elif index == 2:
        return "second"
    elif index == 3:
        return "third"

def user_login_data(f):
    @functools.wraps(f)
    def wrapper(*args,**kwargs):
        user_id = session.get("user_id", None)
        user = None
        if user_id:
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return f(*args,**kwargs)
    return wrapper
