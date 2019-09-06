import re

from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.signing import SignatureExpired
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from itsdangerous import TimedJSONWebSignatureSerializer
from django.conf import settings

from celery_tasks.tasks import send_email_active
from goods.models import GoodsSKU
from order.models import OrderInfo, OrderGoods
from user.models import User, Address, AddressManager
from utils.mixin import LoginRequiredMixin


# def register(request):
#     """用户注册"""
#     return render(request, "register.html")
#
#
# def register_handle(request):
#     """用户注册处理"""
#     user_name = request.POST.get("user_name")
#     pwd = request.POST.get("pwd")
#     email = request.POST.get("email")
#     if not all([user_name, pwd, email]):
#         return render(request, "register.html", {"error": "数据不完整"})
#     if not re.match(r"^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
#         render(request, "register.html", {"error": "邮箱不规范！"})
#     allow = request.POST.get("allow")
#     if allow != "on":
#         return render(request, "register.html", {"error": "请同意协议！"})
#     # 校验用户名是否存在
#     try:
#         user = User.objects.get(username=user_name)
#     except User.DoesNotExist:
#         # 用户名不存在
#         user = None
#     if user:
#         return render(request, "register.html", {"error": "用户已存在！"})
#
#     user = User.objects.create_user(username=user_name, password=pwd, email=email)
#     user.is_active = 0
#     user.save()
#
#     return redirect(reverse("goods:index"))


class registerView(View):
    """用户注册"""

    def get(self, request):
        return render(request, "register.html")

    def post(self, request):
        user_name = request.POST.get("user_name")
        pwd = request.POST.get("pwd")
        email = request.POST.get("email")
        if not all([user_name, pwd, email]):
            return render(request, "register.html", {"error": "数据不完整"})
        if not re.match(r"^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            render(request, "register.html", {"error": "邮箱不规范！"})
        allow = request.POST.get("allow")
        if allow != "on":
            return render(request, "register.html", {"error": "请同意协议！"})
        # 校验用户名是否存在
        try:
            user = User.objects.get(username=user_name)
        except User.DoesNotExist:
            # 用户名不存在
            user = None
        if user:
            return render(request, "register.html", {"error": "用户已存在！"})

        user = User.objects.create_user(username=user_name, password=pwd, email=email)
        user.is_active = 0
        user.save()
        # 使用itsdangous进行生成token
        Serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 3600)
        info = {"confirm": user.id}
        token = Serializer.dumps(info).decode()
        # 发送
        # email_title = '天天生鲜'
        # email_body = '天天生鲜正文'
        # msg = '<a href="http://192.168.58.130:8000/user/active/%s" target="_blank">http://192.168.58.130:8000/user/active/%s</a>' %(token,token)
        # send_status = send_mail(email_title, email_body, settings.EMAIL_FROM,[email], html_message=msg)
        send_email_active.delay(email, token)

        return redirect(reverse("goods:index"))


class ActiveView(View):
    """激活邮件"""

    def get(self, request, token):
        Serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 3600)
        try:
            token = Serializer.loads(token)
            user_id = token["confirm"]
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            return redirect(reverse("user:login"))
        except SignatureExpired as e:
            return HttpResponse("激活链接已失效！")

    def post(self, request):
        pass


class LoginView(View):
    """登录"""

    def get(self, request):
        if "username" in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = "checked"
        else:
            username = ''
            checked = ''
        return render(request, 'login.html', {'username': username, 'checked': checked})

    def post(self, request):
        username = request.POST.get('username')
        pwd = request.POST.get('pwd')
        if not all([username, pwd]):
            return render(request, "login.html", {'error': '参数不全'})
        user = authenticate(username=username, password=pwd)
        if user is not None:
            if user.is_active:
                login(request, user)
                # 获取登录后要跳转的地址,默认跳转到
                url = request.GET.get('next', reverse("goods:index"))
                response = redirect(url)
                remenber = request.POST.get('remenber')
                if remenber == "on":
                    # pass
                    response.set_cookie('username', username, 7 * 24 * 3600)
                else:
                    response.delete_cookie('username')
                return response

            else:
                return render(request, "login.html", {'error': '用户未激活'})

        else:
            return render(request, "login.html", {'error': '用户名或密码错误'})


class Logout(View):
    """退出"""

    def get(self, request):
        logout(request)
        return redirect(reverse("goods:index"))


class UserInfoView(LoginRequiredMixin, View):
    """用户中心-信息页"""

    def get(self, request):
        # 获取用户的个人信息
        user = request.user
        address = Address.objects.get_default_address(user)
        # 获取用户的浏览记录
        from django_redis import get_redis_connection
        connect = get_redis_connection("default")
        history_key = 'history_%s' % user.id
        # 获取用户最新浏览的5个商品
        sku_id = connect.lrange(history_key, 0, 4)
        goods_list = []
        for goods_id in sku_id:
            goods = GoodsSKU.objects.get(id=goods_id)
            goods_list.append(goods)

        context = {
            "page": 'user',
            'address': address,
            'goods_list': goods_list,
        }

        return render(request, 'user_center_info.html', context)


class UserOrderView(LoginRequiredMixin, View):
    """用户中心-订单页"""

    def get(self, request, page):
        user = request.user
        orders = OrderInfo.objects.filter(user=user).order_by('-create_time')
        for order_sku in orders:
            goods_skus = OrderGoods.objects.filter(order=order_sku.order_id)
            for goods_sku in goods_skus:
                amount = goods_sku.price * goods_sku.count
                goods_sku.amount = amount
            # TODO 这里有点不好理解
            order_sku.goods_skus = goods_skus
            order_sku.status_name = OrderInfo.ORDER_STATUS[order_sku.order_status]

        paginator = Paginator(orders, 1)
        # 对接收的页数进行容错处理
        try:
            page = int(page)
        except Exception as e:
            page = 1
        if page > paginator.num_pages:
            page = 1
        sku_pages = paginator.page(page)
        context = {
            'sku_pages': sku_pages,
            "page": 'order'
        }
        return render(request, 'user_center_order.html', context=context)


class UserSiteView(LoginRequiredMixin, View):
    """用户中心-地址页"""

    def get(self, request):
        # request.user.is_authenticated
        user = request.user
        # try:
        #     address = Address.objects.get(user_id=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        # 使用地址模型类管理器获取默认地址

        address = Address.objects.get_default_address(user)
        return render(request, 'user_center_site.html', {"page": 'address', 'address': address})

    def post(self, request):
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'error': '参数不全'})

        if not re.match(r'^1(3|4|5|6|7|8|9)\d{9}', phone):
            return render(request, 'user_center_site.html', {'error': '手机号格式不正确'})

        user = request.user

        # try:
        #     address = Address.objects.get(user_id=user, is_default=True)
        # except Address.DoesNotExist:
        #     address = None
        address = Address.objects.get_default_address(user)

        if address:
            is_default = False
        else:
            is_default = True

        Address.objects.create(user_id=user,
                               reciver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default,
                               )
        return redirect(reverse("user:address"))
