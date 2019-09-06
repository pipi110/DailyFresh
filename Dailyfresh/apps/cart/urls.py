from django.conf.urls import url, include

from cart.views import CartAddView, CartView, CartUpdateView, CartDeleteView

urlpatterns = [
    url(r"^add$", CartAddView.as_view(), name="add"),  # 购物车记录添加
    url(r"^$", CartView.as_view(), name="cart"),  # 购物车记录添加
    url(r"^update$", CartUpdateView.as_view(), name="update"),  # 购物车记录更新
    url(r"^delete$", CartDeleteView.as_view(), name="delete"),  # 购物车记录删除
]
