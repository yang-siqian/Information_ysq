from info import constants
from info.models import News
from info.modules.news import news_blue
from flask import render_template, current_app, g, abort

from info.utils.set_filters import user_login_data


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

    data = {
        "user":user.to_dict() if user else None,
        "news_dict_li":news_dict_li,
        "news":news.to_dict()
    }
    return render_template("news/detail.html",data=data)
