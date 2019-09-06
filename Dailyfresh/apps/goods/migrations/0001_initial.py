# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Goods',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('id_delete', models.BooleanField(verbose_name='逻辑删除', default=False)),
                ('name', models.CharField(verbose_name='商品名称', max_length=20)),
            ],
            options={
                'verbose_name': '商品spu',
                'verbose_name_plural': '商品spu',
                'db_table': 'df_goods',
            },
        ),
        migrations.CreateModel(
            name='GoodsImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('id_delete', models.BooleanField(verbose_name='逻辑删除', default=False)),
                ('image', models.ImageField(verbose_name='商品图片', upload_to='goods')),
            ],
            options={
                'verbose_name': '商品图片',
                'verbose_name_plural': '商品图片',
                'db_table': 'df_goods_image',
            },
        ),
        migrations.CreateModel(
            name='GoodsSKU',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('id_delete', models.BooleanField(verbose_name='逻辑删除', default=False)),
                ('name', models.CharField(verbose_name='商品标题', max_length=20)),
                ('desc', models.CharField(verbose_name='商品介绍', max_length=256)),
                ('price', models.DecimalField(verbose_name='商品价格', max_digits=10, decimal_places=2)),
                ('unite', models.CharField(verbose_name='商品单位', max_length=20)),
                ('image', models.ImageField(verbose_name='商品图片', upload_to='goods')),
                ('stock', models.IntegerField(verbose_name='商品库存', default=1)),
                ('sales', models.IntegerField(verbose_name='商品销量', default=0)),
                ('status', models.SmallIntegerField(verbose_name='商品状态', default=1, choices=[(0, '下线'), (1, '上线')])),
                ('goods', models.ForeignKey(verbose_name='商品对应的spu', to='goods.Goods')),
            ],
            options={
                'verbose_name': '商品sku',
                'verbose_name_plural': '商品sku',
                'db_table': 'df_goods_sku',
            },
        ),
        migrations.CreateModel(
            name='GoodsType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('id_delete', models.BooleanField(verbose_name='逻辑删除', default=False)),
                ('name', models.CharField(verbose_name='商品种类', max_length=20)),
                ('logo', models.CharField(verbose_name='logo', max_length=20)),
                ('picture', models.ImageField(verbose_name='图片', upload_to='type')),
            ],
            options={
                'verbose_name': '商品种类',
                'verbose_name_plural': '商品种类',
                'db_table': 'df_goods_type',
            },
        ),
        migrations.CreateModel(
            name='IndexGoodsBanner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('id_delete', models.BooleanField(verbose_name='逻辑删除', default=False)),
                ('image', models.ImageField(verbose_name='商品图片', upload_to='banner')),
                ('index', models.SmallIntegerField(verbose_name='排序', default=0)),
                ('sku', models.ForeignKey(verbose_name='商品id', to='goods.GoodsSKU')),
            ],
            options={
                'verbose_name': '首页轮播图',
                'verbose_name_plural': '首页轮播图',
                'db_table': 'df_index_goods_banner',
            },
        ),
        migrations.CreateModel(
            name='IndexPromotionBanner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('id_delete', models.BooleanField(verbose_name='逻辑删除', default=False)),
                ('name', models.CharField(verbose_name='活动名称', max_length=20)),
                ('image', models.ImageField(verbose_name='活动图片', upload_to='banner')),
                ('url', models.URLField(verbose_name='活动url')),
                ('index', models.SmallIntegerField(verbose_name='排序', default=0)),
            ],
            options={
                'verbose_name': '首页商品促销',
                'verbose_name_plural': '首页商品促销',
                'db_table': 'df_index_promotion',
            },
        ),
        migrations.CreateModel(
            name='IndexTypeGoodsBanner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('create_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('update_time', models.DateTimeField(verbose_name='创建时间', auto_now_add=True)),
                ('id_delete', models.BooleanField(verbose_name='逻辑删除', default=False)),
                ('is_show', models.SmallIntegerField(verbose_name='商品图片', default=1, choices=[(0, '标题'), (1, '图片')])),
                ('index', models.SmallIntegerField(verbose_name='排序', default=0)),
                ('sku', models.ForeignKey(verbose_name='商品id', to='goods.GoodsSKU')),
                ('type', models.ForeignKey(verbose_name='种类id', to='goods.GoodsType')),
            ],
            options={
                'verbose_name': '首页分类商品',
                'verbose_name_plural': '首页分类商品',
                'db_table': 'df_index_type_goods',
            },
        ),
        migrations.AddField(
            model_name='goodssku',
            name='type',
            field=models.ForeignKey(verbose_name='商品所属种类', to='goods.GoodsType'),
        ),
        migrations.AddField(
            model_name='goodsimage',
            name='goods',
            field=models.ForeignKey(verbose_name='商品id', to='goods.GoodsSKU'),
        ),
    ]
