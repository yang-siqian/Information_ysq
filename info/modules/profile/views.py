from flask import render_template, g, redirect, request

from info.modules.profile import profile_blue
from info.utils.set_filters import user_login_data


@profile_blue.route("/base_info",methods=["GET", "POST"])
@user_login_data
def base_info():
    if request.method=="GET":
        return render_template("news/user_base_info.html", data={"user": g.user.to_dict()})


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