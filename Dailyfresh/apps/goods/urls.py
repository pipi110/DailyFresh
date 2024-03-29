from django.conf.urls import url, include

from goods import views
from goods.views import IndexView, DetailView, ListView

urlpatterns = [
    url(r"^$", IndexView.as_view(), name="index"),  # 首页
    url(r"^detail/(?P<good_id>\d+)$", DetailView.as_view(), name="detail"), # 商品详情页
    url(r"^list/(?P<type_id>\d+)/(?P<page>\d+)/$", ListView.as_view(), name="list")  # 商品列表页
]
