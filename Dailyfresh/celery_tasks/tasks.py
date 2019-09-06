import time
import os
import django

from celery import Celery
from django.conf import settings
from django.core.mail import send_mail
from django.template import loader, RequestContext

# django环境的初始化

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Dailyfresh.settings")
django.setup()

from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner

# 这个顺序不能乱放，不然报错原因不好找
app = Celery("celery_tasks.tasks", broker="redis://127.0.0.1:6379/2")
"""
启动命令：celery -A celery_tasks.tasks worker -l info

"""


@app.task
def send_email_active(email, token):
    """发生短信的异步操作"""
    email_title = '天天生鲜'
    email_body = '天天生鲜正文'
    msg = '<a href="http://192.168.58.131:8000/user/active/%s" target="_blank">http://192.168.58.131:8000/user/active/%s</a>' % (
        token, token)
    send_status = send_mail(email_title, email_body, settings.EMAIL_FROM, [email], html_message=msg)
    # time.sleep(5)


@app.task
def generate_static_index_html():
    # 获取商品种类的信息
    types = GoodsType.objects.all()
    # 获取banner图的信息
    banners = IndexGoodsBanner.objects.all().order_by('index')  # 默认生序
    # 获取促销广告的信息
    promotions = IndexPromotionBanner.objects.all().order_by('index')
    # 获取首页分类商品的信息
    for type in types:
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, is_show=1).order_by('index')
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, is_show=0).order_by('index')
        # 给type动态的添加属性
        type.image_banners = image_banners
        type.title_banners = title_banners

    context = {
        'types': types,
        'banners': banners,
        'promotions': promotions
    }
    temp = loader.get_template('index_static.html')

    static_index_html = temp.render(context=context)

    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_index_html)
