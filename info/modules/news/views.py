from info import constants
from info.models import News
from info.modules.news import news_blue
from flask import render_template, current_app


@news_blue.route('/<int:news_id>')
def news_detail(news_id):
    """
    新闻详情
    :param news_id:
    :return:
    """

    # 右侧新闻排行的逻辑实现
    news_list = []
    try:
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    news_dict_li = []
    for news in news_list:
        news_dict_li.append(news.to_basic_dict())

    data = {
        "news_dict_li":news_dict_li
    }
    return render_template("news/detail.html",data=data)