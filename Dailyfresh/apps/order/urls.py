from django.conf.urls import url, include

from order.views import OrderPlaceView, OrderCommitView, OrderPayView, OrderCheckView

urlpatterns = [
    url(r"^place$", OrderPlaceView.as_view(), name="place"),  # 订单详情
    url(r"^commit$", OrderCommitView.as_view(), name="commit"),  # 订单详情
    url(r"^pay$", OrderPayView.as_view(), name="pay"),  # 订单详情
    url(r"^check$", OrderCheckView.as_view(), name="check"),  # 订单详情
]
