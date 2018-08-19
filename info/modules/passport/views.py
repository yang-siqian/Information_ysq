from flask import request, abort, current_app, make_response

from info import redis_store, constants
from . import passport_blue
from info.utils.captcha.captcha import captcha

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