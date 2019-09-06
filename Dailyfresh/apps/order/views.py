from datetime import datetime
import os

from django.http import JsonResponse
from django.shortcuts import render
from django.conf import settings
# Create your views here.
from django.views.generic.base import View
from django_redis import get_redis_connection
from django.db import transaction
from goods.models import GoodsSKU
from order.models import OrderInfo, OrderGoods
from user.models import Address
from utils.mixin import LoginRequiredMixin
from alipay import AliPay


class OrderPlaceView(LoginRequiredMixin, View):
    """购物车记录添加"""

    def post(self, request):
        sku_ids = request.POST.getlist('sku_id')
        user = request.user
        cart_key = 'cart_%d' % user.id
        conn = get_redis_connection('default')
        total_count = 0
        total_amount = 0
        skus = []
        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=sku_id)
            count = conn.hget(cart_key, sku_id)
            amount = sku.price * int(count)
            sku.count = count
            sku.amount = amount
            skus.append(sku)
            total_count += int(count)
            total_amount += amount

        # 邮费
        postage = 10
        total_pay = postage + total_amount
        address = Address.objects.filter(user_id=user)
        sku_ids = ','.join(sku_ids)
        context = {
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'postage': postage,
            'total_pay': total_pay,
            'address': address,
            'sku_ids': sku_ids
        }
        return render(request, 'place_order.html', context=context)


class OrderCommitView(View):
    """订单提交"""

    @transaction.atomic
    def post(self, request):
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'error': '请先登录'})
        addr = request.POST.get('addr')
        pay_method = request.POST.get('pay_method')
        sku_ids = request.POST.get('sku_ids')

        if not all([addr, pay_method, sku_ids]):
            return JsonResponse({'res': 0, 'error': '参数不完整'})
        try:
            addr = Address.objects.get(id=addr)
        except Address.DoesNotExist:
            return JsonResponse({'res': 0, 'error': '地址无效'})
        if pay_method not in OrderInfo.PAY_METHODS.keys():
            return JsonResponse({'res': 0, 'error': '非法的支付方式'})

        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)
        transit_price = 10
        total_count = 0
        total_price = 0
        save_id = transaction.savepoint()
        try:
            order_info = OrderInfo.objects.create(order_id=order_id,
                                                  addr=addr,
                                                  user=user,
                                                  pay_method=pay_method,
                                                  total_count=total_count,
                                                  total_price=total_price,
                                                  transit_price=transit_price,
                                                  )
            sku_ids = sku_ids.split(',')
            for sku_id in sku_ids:
                for i in range(3):
                    try:
                        # sku = GoodsSKU.objects.select_for_update().get(id=sku_id) # 悲观锁的实现方式
                        sku = GoodsSKU.objects.get(id=sku_id)
                    except GoodsSKU.DoesNotExist:
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'res': 0, 'error': '商品不存在'})
                    cart_key = 'cart_%d' % user.id
                    conn = get_redis_connection('default')
                    count = conn.hget(cart_key, sku_id)
                    if int(count) > sku.stock:
                        transaction.savepoint_rollback(save_id)
                        return JsonResponse({'res': 0, 'error': '商品库存不足'})
                    # 库存和销量更新
                    # 乐观锁的实现方式
                    origin_stock = sku.stock
                    new_stock = sku.stock - int(count)
                    new_sales = sku.stock - int(count)
                    res = GoodsSKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock,
                                                                                        sales=new_sales)
                    if res == 0:
                        if i == 2:
                            transaction.savepoint_rollback(save_id)
                            return JsonResponse({'res': 0, 'error': '下单失败2'})
                        continue

                    OrderGoods.objects.create(sku=sku,
                                              order=order_info,
                                              count=count,
                                              price=sku.price
                                              )

                    amount = sku.price * int(count)
                    total_count += int(count)
                    total_price += amount
                    # 跳出循环
                    break

            order_info.total_count = total_count
            order_info.total_price = total_price
            order_info.save()
        except Exception as e:
            transaction.savepoint_rollback(save_id)
            return JsonResponse({'res': 0, 'error': '下单失败'})
        transaction.savepoint_commit(save_id)
        # 清除购物车数据
        conn.hdel(cart_key, *sku_ids)
        return JsonResponse({'res': 1, 'msg': '创建成功'})


class OrderPayView(View):
    """订单支付"""

    def post(self, request):
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'error': '请登录'})
        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({'res': 0, 'error': '无效的订单'})
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=3,
                                          order_status=1
                                          )
        except Exception as e:
            return JsonResponse({'res': 0, 'error': '订单不存在'})
        alipay = AliPay(
            appid="2016091300505019",
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem'),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )
        total_pay = order.total_price + order.transit_price
        order_string = alipay.api_alipay_trade_page_pay(
            out_trade_no=order_id,
            total_amount=str(total_pay),
            subject='天天生鲜_%s' % order_id,
            return_url=None,
            notify_url=None  # 可选, 不填则使用默认notify url
        )
        pay_url = "https://openapi.alipaydev.com/gateway.do?" + order_string
        return JsonResponse({'res': 1, 'msg': '成功', 'pay_url': pay_url})


class OrderCheckView(View):
    """"""

    def post(self, request):
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'error': '请登录'})
        order_id = request.POST.get('order_id')
        if not order_id:
            return JsonResponse({'res': 0, 'error': '无效的订单'})
        try:
            order = OrderInfo.objects.get(order_id=order_id,
                                          user=user,
                                          pay_method=3,
                                          order_status=1
                                          )
        except Exception as e:
            return JsonResponse({'res': 0, 'error': '订单不存在'})
        alipay = AliPay(
            appid="2016091300505019",
            app_notify_url=None,  # 默认回调url
            app_private_key_path=os.path.join(settings.BASE_DIR, 'apps/order/app_private_key.pem'),
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_path=os.path.join(settings.BASE_DIR, 'apps/order/alipay_public_key.pem'),
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )
        while True:
            response = alipay.api_alipay_trade_query(order_id)
            code = response.get('code')
            if code == '10000' and response.get('trade_status') == 'TRADE_SUCCESS':
                # 支付成功
                trade_no = response.get('trade_no')
                order.trade_no = trade_no
                order.order_status = 4  # 待评价
                order.save()
                return JsonResponse({'res': 1, 'error': '支付成功'})
            elif code == '40004' or (code == '10000' and response.get('trade_status') == 'WAIT_BUYER_PAY'):
                # 等待买家付款
                # code == '40004'业务处理失败，再次发送请求
                import time
                time.sleep(5)
                continue
            else:
                return JsonResponse({'res': 0, 'error': '支付出错'})
