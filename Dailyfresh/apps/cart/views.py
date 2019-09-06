from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views.generic.base import View
from django_redis import get_redis_connection

from goods.models import GoodsSKU
from utils.mixin import LoginRequiredMixin


class CartAddView(View):
    """购物车添加"""

    def post(self, request):
        user = request.user
        # 这里不用login_required的原因是ajax返回的
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'error': '请先登录'})
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        if not all([sku_id, count]):
            return JsonResponse({'res': 0, 'error': '数据不完整'})
        # 个人觉得这里不用校验
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 0, 'error': '商品数目出错'})
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except Exception as e:
            return JsonResponse({'res': 0, 'error': '商品不存在'})
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        # 如果拿不到，返回none
        cart_count = conn.hget(cart_key, sku_id)
        if cart_count:
            count += int(cart_count)
        if count > sku.stock:
            return JsonResponse({'res': 0, 'error': '商品库存不足'})
        conn.hset(cart_key, sku_id, count)
        # 获取购物车总数
        total_count = conn.hlen(cart_key)
        return JsonResponse({'res': 1, 'msg': '购物车记录添加成功', 'total_count': total_count})


class CartView(LoginRequiredMixin, View):
    """购物车记录查看"""

    def get(self, request):
        user = request.user
        cart_key = 'cart_%d' % user.id
        conn = get_redis_connection('default')
        cart_dict = conn.hgetall(cart_key)
        skus = []
        total_price = 0
        total_count = 0
        for sku_id, count in cart_dict.items():
            sku = GoodsSKU.objects.get(id=sku_id)
            amount = sku.price * int(count)
            # 给对象动态添加属性
            sku.amount = amount
            sku.count = count
            skus.append(sku)
            total_price += amount
            total_count += int(count)
        context = {
            'total_price': total_price,
            'total_count': total_count,
            'skus': skus,
        }
        # print(context)
        return render(request, 'cart.html', context=context)


class CartUpdateView(View):
    """购物车记录更新"""

    def post(self, request):
        # 这里不用login_required的原因是ajax返回的
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'error': '请先登录'})
        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        if not all([sku_id, count]):
            return JsonResponse({'res': 0, 'error': '数据不完整'})
        # 个人觉得这里不用校验
        try:
            count = int(count)
        except Exception as e:
            return JsonResponse({'res': 0, 'error': '商品数目出错'})
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except Exception as e:
            return JsonResponse({'res': 0, 'error': '商品不存在'})
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        if count > sku.stock:
            return JsonResponse({'res': 0, 'error': '商品库存不足'})
        conn.hset(cart_key, sku_id, count)
        vals = conn.hvals(cart_key)
        total_count = 0
        for val in vals:
            total_count += int(val)
        return JsonResponse({'res': 1, 'msg': '购物车记录更新成功', 'total_count': total_count})


class CartDeleteView(View):
    """购物车记录删除"""

    def post(self, request):
        user = request.user
        if not user.is_authenticated():
            return JsonResponse({'res': 0, 'error': '请先登录'})
        sku_id = request.POST.get('sku_id')
        try:
            sku = GoodsSKU.objects.get(id=sku_id)
        except Exception as e:
            return JsonResponse({'res': 0, 'error': '商品不存在'})
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        conn.hdel(cart_key, sku_id)
        vals = conn.hvals(cart_key)
        total_count = 0
        for val in vals:
            total_count += int(val)
        return JsonResponse({'res': 1, 'msg': '购物车记录删除成功', 'total_count': total_count})
