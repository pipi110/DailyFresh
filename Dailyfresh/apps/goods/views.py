from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic.base import View
from django_redis import get_redis_connection

from goods.models import GoodsType, IndexGoodsBanner, IndexPromotionBanner, IndexTypeGoodsBanner, GoodsSKU
from order.models import OrderGoods


class IndexView(View):
    """首页"""

    def get(self, request):
        """显示首页"""
        context = cache.get('index_page_data')
        # 获取商品种类的信息
        if context is None:
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
                'promotions': promotions,
            }

            # 设置缓存
            cache.set('index_page_data', context, 3600)
        # 购物车数量
        cart_count = 0
        user = request.user
        if user.is_authenticated():
            # 用户已登录
            cart_key = 'cart_%d' % user.id
            conn = get_redis_connection('default')
            cart_count = conn.hlen(cart_key)

        context.update(cart_count=cart_count)

        return render(request, "index.html", context=context)


class DetailView(View):
    """商品详情页"""

    def get(self, request, good_id):
        try:
            sku = GoodsSKU.objects.get(id=good_id)
        except GoodsSKU.DoesNotExist:
            return redirect(reverse('goods:index'))
        types = GoodsType.objects.all()
        # 评论
        comments = OrderGoods.objects.filter(sku=sku).exclude(comment='')

        # 左下角推荐的类型
        news_types = GoodsSKU.objects.filter(type=sku.type).order_by('-create_time')[:2]
        # 同种商品不同种类的
        other_skus = GoodsSKU.objects.filter(goods=sku.goods).exclude(id=good_id)
        cart_count = 0
        user = request.user
        if user.is_authenticated():
            # 用户已登录
            cart_key = 'cart_%d' % user.id
            conn = get_redis_connection('default')
            cart_count = conn.hlen(cart_key)

            history_key = 'history_%d' % user.id
            conn.lrem(history_key, 0, good_id)
            conn.lpush(history_key, good_id)
            conn.ltrim(history_key, 0, 4)

        context = {
            'sku': sku,
            'types': types,
            'comments': comments,
            'news_types': news_types,
            'other_skus': other_skus,
            'cart_count': cart_count
        }
        return render(request, 'detail.html', context=context)


class ListView(View):
    """列表页"""

    def get(self, request, type_id, page):
        try:
            goods_type = GoodsType.objects.get(id=type_id)
        except GoodsType.DoesNotExist:
            return redirect(reverse('goods:index'))
        # 获取排序的方式
        sort = request.GET.get('sort')
        if sort == 'hot':
            skus = GoodsSKU.objects.all().order_by('-sales')
        elif sort == 'price':
            skus = GoodsSKU.objects.all().order_by('price')
        else:
            sort = 'default'
            skus = GoodsSKU.objects.filter(type=goods_type).order_by('-id')

        paginator = Paginator(skus, 1)
        # 对接收的页数进行容错处理
        try:
            page = int(page)
        except Exception as e:
            page = 1
        if page > paginator.num_pages:
            page = 1
        sku_pages = paginator.page(page)
        # 所有商品的分类
        types = GoodsType.objects.all()
        # 左下角推荐的类型
        news_types = GoodsSKU.objects.filter(type=goods_type).order_by('-create_time')[:2]
        cart_count = 0
        user = request.user
        if user.is_authenticated():
            # 用户已登录
            cart_key = 'cart_%d' % user.id
            conn = get_redis_connection('default')
            cart_count = conn.hlen(cart_key)
        context = {
            'goods_type': goods_type,
            'types': types,
            'sku_pages': sku_pages,
            'news_types': news_types,
            'cart_count': cart_count,
            'sort': sort
        }
        return render(request, 'list.html', context=context)
