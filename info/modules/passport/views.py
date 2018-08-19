import random
import re
from datetime import datetime

from flask import request, abort, current_app, make_response, jsonify, session
from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.utils.response_code import RET
from . import passport_blue
from info.utils.captcha.captcha import captcha

@passport_blue.route("/register",methods=["POST"])
def register():
    """
    1.获取参数
    2.校验参数
    3.从服务器取得真实的短信验证码内容
    4.与用户短信验证码内容进行对比，如果比对不一致，返回验证码错误
    5.如果一致，初始化User模型，并且属性
    6.将User模型添加到数据库
    7.返回响应
    """
    #  1.获取参数
    param_dict = request.json
    mobile = request.json.get('mobile')
    smscode = request.json.get('smscode')
    password = request.json.get('password')

    #  2.校验参数
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    # 校验手机号是否正确
    if not re.match("1[35678]\\d{9}", mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

    #  3.从服务器取得真实的短信验证码内容
    try:
        real_sms_code = redis_store.get("SMS_" + mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询失败")
    if not real_sms_code:
        return jsonify(errno=RET.NODATA,errmsg="短信验证码已过期")

    # 4.与用户短信验证码内容进行对比，如果比对不一致，返回验证码错误
    if real_sms_code != smscode:
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5.如果一致，初始化User模型，并且属性
    user = User()
    user.mobile = mobile
    # 暂时没有昵称用手机号代替
    user.nick_name = mobile
    # 记录用户最后一次登录时间
    user.last_login = datetime.now()

    # TODO 对密码做处理

    # 6.将User模型添加到数据库
    try:
        db.session.set(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")

    # 往session中保存数据表示当前已登录
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick-name'] = user.nick_name

    # 7.返回响应
    return jsonify(errno=RET.OK,errmsg="注册成功")



@passport_blue.route("/sms_code",methods=["POST"])
def send_sms_code():
    """
    发送短信逻辑：
    1.获取参数：手机号，图片验证码内容，图片验证码编号
    2.校验参数（判断参数是否有值，是否符合规则）
    3.先从redis取出真实的验证码内容
    4.与用户验证码内容进行对比，如果比对不一致，返回验证码错误
    5.如果一致，生成验证码的内容（随机数据）
    6.发送短信验证码
    7.告知发送结果
    """
    # 1.获取参数：手机号，图片验证码内容，图片验证码编号
    # params_dict = json.load(request.data)
    params_dict = request.json
    mobile = params_dict.get("mobile")
    image_code = params_dict.get("image_code")
    image_code_id = params_dict.get("image_code_id")

    # 2.校验参数（判断参数是否有值，是否符合规则）
    # 判断参数是否有值
    if not all([mobile, image_code, image_code_id]):
        # {errno="4100", errmsg="参数有误"}
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")
    # 校验手机号是否正确
    if not re.match("1[35678]\\d{9}",mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")
    # 3.先从redis取出真实的验证码内容
    try:
        real_image_code = redis_store.get("ImageCodeId_"+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="数据查询失败")
    if not real_image_code:
        return jsonify(errno=RET.NODATA,errmsg="图片验证码已过期")

    # 4.与用户验证码内容进行对比，如果比对不一致，返回验证码错误
    if real_image_code.decode().upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5.如果一致，生成验证码的内容（随机数据）
    # 随机数字，保证数字长度为6，不够在前面用0补
    sms_code_str = "%06d"% random.randint(0,999999)
    current_app.logger.debug("短信验证码的内容是：%s"% sms_code_str)

    # 6.发送短信验证码
    #mobie:手机号  sms_code_str：验证码内容  SMS_CODE_REDIS_EXPIRES/5：短信验证码有效期60秒  选用模板为1
    result = CCP().send_template_sms(mobile,[sms_code_str,constants.SMS_CODE_REDIS_EXPIRES/5],'1')
    if result != 0:
        # 代表发送不成功
        return jsonify(errno=RET.THIRDERR,errmsg="短信发送失败")
     # 保存验证码内容到Redis
    try:
        redis_store.set("SMS_"+mobile,sms_code_str,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存失败")
    # 7.告知发送结果
    return jsonify(errno=RET.OK,errmsg="短信发送成功")



@passport_blue.route("/image_code")
def get_image_code():
    """生成图片验证码并返回"""
    # 1.取到参数
    # args:取到url中？后面的参数
    image_code_id = request.args.get("imageCodeId",None)
    # 2.判断参数是否有值
    if not image_code_id:
        return abort(403)
    # 3.生成图片验证码
    name, text, image = captcha.generate_captcha()
    print(text)

    # 4.保存图片验证码文字内容到Redis
    try:
        redis_store.set("ImageCodeId_"+image_code_id,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        # 500以上的是服务器错误
        abort(500)

    # 5.返回验证码图片
    response = make_response(image)
    # 设置数据类型，以便浏览器智能识别是什么类型
    response.headers["Content-Type"] = "image/jpg"
    return response