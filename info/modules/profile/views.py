from flask import render_template, g, redirect, request, jsonify, current_app, abort

from info import db, constants
from info.constants import QINIU_DOMIN_PREFIX
from info.models import Category, News, User
from info.modules.profile import profile_blue
from info.utils.image_storage import storage
from info.utils.response_code import RET
from info.utils.set_filters import user_login_data


@profile_blue.route('/other_news_list')
def other_news_list():
    # 获取页数
    p = request.args.get("p", 1)
    user_id = request.args.get("user_id")
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if not all([p, user_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not user:
        return jsonify(errno=RET.NODATA, errmsg="用户不存在")

    try:
        paginate = News.query.filter(News.user_id == user.id).paginate(p, constants.OTHER_NEWS_PAGE_MAX_COUNT, False)
        # 获取当前页数据
        news_li = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    news_dict_li = []

    for news_item in news_li:
        news_dict_li.append(news_item.to_review_dict())
    data = {"news_list": news_dict_li, "total_page": total_page, "current_page": current_page}
    return jsonify(errno=RET.OK, errmsg="OK", data=data)



@profile_blue.route("/other_info")
@user_login_data
def other_info():
    """查看其他用户信息"""
    user = g.user

    user_id = request.args.get("user_id")
    if not user_id:
        abort(404)

    other = None
    try:
        other = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
    if not other:
        abort(404)

    is_followed = False
    if g.user:
        if other.followers.filter(User.id == user.id).count()>0:
            is_followed = True

    data = {
        "user":user.to_dict(),
        "other":other.to_dict(),
        "is_followed":is_followed
    }
    return render_template("news/other.html", data=data)


@profile_blue.route("/user_follow")
@user_login_data
def user_follow():
    p = request.args.get("p",1)
    try:
        p=int(p)
    except Exception as e:
        current_app.logger.error(e)
        p=1

    user = g.user
    follows=[]
    current_page = 1
    total_page = 1

    try:
        paginate = user.followers.paginate(p,constants.USER_FOLLOWED_MAX_COUNT,False)
        follows = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    user_dict_li = []
    for follow_user in follows:
        user_dict_li.append(follow_user.to_dict())

    data={
        "users":user_dict_li,
        "total_page":total_page,
        "current_page":current_page
    }
    return render_template("news/user_follow.html", data=data)







@profile_blue.route('/news_list')
@user_login_data
def news_list():
    # 获取页数
    p = request.args.get("p", 1)
    try:
        p = int(p)
    except Exception as e:
        current_app.logger.error(e)
        p = 1

    user = g.user
    news_li = []
    current_page = 1
    total_page = 1
    try:
        paginate = News.query.filter(News.user_id == user.id).paginate(p, constants.USER_COLLECTION_MAX_NEWS, False)
        # 获取当前页数据
        news_li = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []

    for news_item in news_li:
        news_dict_li.append(news_item.to_review_dict())
    data = {
        "news_list": news_dict_li,
        "total_page": total_page,
        "current_page": current_page
        }
    return render_template('news/user_news_list.html', data=data)


@profile_blue.route('/news_release',methods=["GET","POST"])
@user_login_data
def news_release():
    if request.method == "GET":
        categories = []
        try:
            # 获取所有的分类数据
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)

        # 定义列表保存分类数据
        categories_dicts = []

        for category in categories:
            # 获取字典
            cate_dict = category.to_dict()
            # 拼接内容
            categories_dicts.append(cate_dict)

        # 移除`最新`分类
        categories_dicts.pop(0)
        # 返回内容
        return render_template('news/user_news_release.html', data={"categories": categories_dicts})

        # 1. 获取要提交的数据
    title = request.form.get("title")
    source = "个人发布"
    digest = request.form.get("digest")
    content = request.form.get("content")
    index_image = request.files.get("index_image")
    category_id = request.form.get("category_id")
    # 1.1 判断数据是否有值
    if not all([title, source, digest, content, index_image, category_id]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 1.2 尝试读取图片
    try:
        index_image = index_image.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 2. 将标题图片上传到七牛
    try:
        key = storage(index_image)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")

    # 3. 初始化新闻模型，并设置相关数据
    news = News()
    news.title = title
    news.digest = digest
    news.source = source
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = g.user.id
    # 1代表待审核状态
    news.status = 1

    # 4. 保存到数据库
    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    # 5. 返回结果
    return jsonify(errno=RET.OK, errmsg="发布成功，等待审核")



@profile_blue.route("/collection")
@user_login_data
def user_collection():
    page = request.args.get("p",1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    user = g.user
    current_page = 1
    total_page = 1
    news_list = []
    try:
        paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
        current_page = paginate.page
        total_page = paginate.pages
        news_list = paginate.items
    except Exception as e:
        current_app.logger.error(e)

    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())


    data={
        "total_page": total_page,
        "current_page": current_page,
        "collections": news_dict_li
    }
    return render_template("news/user_collection.html", data=data)



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