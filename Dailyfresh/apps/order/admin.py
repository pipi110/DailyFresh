from django.contrib import admin

# Register your models here.
from order.models import OrderGoods


admin.site.register(OrderGoods)