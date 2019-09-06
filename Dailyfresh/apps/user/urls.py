from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

from user import views
from user.views import registerView, ActiveView, LoginView, UserInfoView, UserOrderView, UserSiteView, Logout

urlpatterns = [
    # url(r"^register$", views.register, name="register"),
    # url(r"^register_handle$", views.register_handle, name="register_handle"),
    url(r"^register$", registerView.as_view(), name="register"),  # 注册
    url(r"^active/(?P<token>.*?)$", ActiveView.as_view(), name="active"),  # 激活
    url(r"^login$", LoginView.as_view(), name="login"),  # 登录
    url(r"^logout$", Logout.as_view(), name="logout"),  # 退出
    url(r"^$", login_required(UserInfoView.as_view()), name="user"),  # 用户中心信息页
    url(r"^order/(?P<page>\d+)$", login_required(UserOrderView.as_view()), name="order"),  # 用户中心订单页
    url(r"^address$", login_required(UserSiteView.as_view()), name="address"),  # 用户中心地址页
]
