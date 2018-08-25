from flask import render_template, g, redirect, request, jsonify, current_app

from info import db
from info.constants import QINIU_DOMIN_PREFIX
from info.modules.profile import profile_blue
from info.utils.image_storage import storage
from info.utils.response_code import RET
from info.utils.set_filters import user_login_data


@profile_blue.route("/pass_info",methods=["GET", "POST"])
@user_login_data
def pass_info():
    user = g.user
    if request.method == "GET":
        return render_template("news/user_pass_info.html", data={"user": user.to_dict()})

    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if not all([old_password,new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if not user.check_passowrd(old_password):
        return jsonify(errno=RET.PWDERR, errmsg="原密码错误")

    user.password = new_password
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    return jsonify(errno=RET.OK, errmsg="保存成功")



@profile_blue.route("/pic_info",methods=["GET", "POST"])
@user_login_data
def pic_info():
    user = g.user
    if request.method == "GET":
        return render_template("news/user_pic_info.html", data={"user": user.to_dict()})

    try:
        avatar = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        key = storage(avatar)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传头像失败")

    user.avatar_url = key
    return jsonify(errno=RET.OK, errmsg="OK", data={"avatar_url":QINIU_DOMIN_PREFIX+key})



@profile_blue.route("/base_info",methods=["GET", "POST"])
@user_login_data
def base_info():
    if request.method == "GET":
        return render_template("news/user_base_info.html", data={"user": g.user.to_dict()})
    nick_name = request.json.get("nick_name")
    signature = request.json.get("signature")
    gender = request.json.get("gender")

    if not all([nick_name,signature,gender]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")
    if gender not in ("MAN", "WOMAN"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    user = g.user
    user.signature = signature
    user.nick_name = nick_name
    user.gender = gender

    return jsonify(errno=RET.OK, errmsg="OK")


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