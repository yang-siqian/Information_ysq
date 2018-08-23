from info import constants, db
from info.models import News, Comment, CommentLike
from info.modules.news import news_blue
from flask import render_template, current_app, g, abort, jsonify, request

from info.utils.response_code import RET
from info.utils.set_filters import user_login_data

@news_blue.route("/comment_like", methods=['POST'])
@user_login_data
def comment_like():
    """评论点赞"""
    # 1.获取参数
    user = g.user
    comment_id = request.json.get("comment_id")
    news_id = request.json.get("news_id")
    action = request.json.get("action")
    # 2.校验参数
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    if not all([news_id, comment_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ["add", "remove"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        comment_id = int(comment_id)
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 3.查询评论数据
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not comment:
        return jsonify(errno=RET.NODATA, errmsg="评论不存在")

    # 4.添加点赞和取消点赞
    if action == "add":
        comment_like_model = CommentLike.query.filter(CommentLike.user_id == user.id,CommentLike.comment_id == comment.id).first()
        if not comment_like_model:
            comment_like_model = CommentLike()
            comment_like_model.user_id = user.id
            comment_like_model.comment_id = comment_id
            db.session.add(comment_like_model)

    else:
        comment_like_model = CommentLike.query.filter(CommentLike.user_id==user.id,CommentLike.comment_id==comment.id).first()
        if comment_like_model:
            db.session.delete(comment_like_model)
            comment.like_count -= 1

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库操作失败")
    return jsonify(errno=RET.OK, errmsg="操作成功")

@news_blue.route("/news_collect", methods=['POST'])
@user_login_data
def news_collect():
    """新闻收藏"""
    # 1.获取参数
    user = g.user

    news_id = request.json.get("news_id")
    action = request.json.get("action")
    # 2.校验参数
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")

    if not news_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ("collect", "cancel_collect"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 3.查询数据
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    if not news:
        return jsonify(errno=RET.NODATA, errmsg="新闻数据不存在")

    # 4.向数据库添加收藏和取消收藏
    if action == "collect":
        user.collection_news.append(news)
    else:
        user.collection_news.remove(news)

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="保存失败")
    return jsonify(errno=RET.OK, errmsg="操作成功")


@news_blue.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    新闻详情
    :param news_id:
    :return:
    """
    # 查询用户登录信息
    user = g.user


    # 右侧新闻排行的逻辑实现
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    # 查询新闻数据
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        abort(404)
    # 更新点击次数
    news.clicks += 1
    # 判断是否收藏该新闻，默认值为 false
    is_collected = False
    # 判断用户是否收藏过该新闻
    if g.user:
        if news in g.user.collection_news:
            is_collected = True

    # 查询评论数据
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)

    comment_like_ids=[]
    if g.user:
        try:
            # 查询当前用户在当前新闻里点赞了哪些评论
            # 1.查询到当前新闻的所有评论
            comment_ids = [comment.id for comment in comments]
            # 2.查询当前所有评论有哪些被当前用户点赞
            comment_likes = CommentLike.query.filter(CommentLike.comment_id.in_(comment_ids),CommentLike.user_id == g.user.id).all()
            # 3.取到被点赞的评论ID
            comment_like_ids = [comment_like.comment_id for comment_like in comment_likes ]
        except Exception as e:
            current_app.logger.error(e)

    comment_dict_li = []
    for comment in comments:
        comment_dict = comment.to_dict()
        # 代表没有点赞
        comment_dict['is_like'] = False
        # 判断当前遍历到的评论是否被当前登录用户所点赞
        if comment.id in comment_like_ids:
            comment_dict['is_like'] = True
        comment_dict_li.append(comment_dict)


    data = {
        "user":user.to_dict() if user else None,
        "news_dict_li":news_dict_li,
        "is_collected": is_collected,
        "news":news.to_dict(),
        "comments":comment_dict_li
    }
    return render_template("news/detail.html",data=data)
