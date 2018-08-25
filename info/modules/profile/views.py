from flask import render_template, g, redirect

from info.modules.profile import profile_blue
from info.utils.set_filters import user_login_data


@profile_blue.route("/info")
@user_login_data
def user_info():
    user = g.user
    if not user:
        return redirect("/")
    data={
        "user":user.to_dict(),
    }
    return render_template("news/user.html",data=data)