from django.contrib.auth.models import AbstractUser
from django.db import models

from db.base_model import BaseModel


class User(AbstractUser, BaseModel):
    """用户模型类"""

    class Meta:
        db_table = "df_user"
        verbose_name = "用户"
        verbose_name_plural = verbose_name


class AddressManager(models.Manager):
    """地址模型类管理器"""
    def get_default_address(self,user):
        """获取用户的默认地址"""
        # self.model:获取self对象所在的模型类
        try:
            address = self.get(user_id=user, is_default=True) # address = Address.objects.get(user_id=user, is_default=True)
        except self.model.DoesNotExist:
            address = None
        return address


class Address(BaseModel):
    """地址模型类"""
    user_id = models.ForeignKey("User", verbose_name="所属账户")
    reciver = models.CharField(max_length=20, verbose_name="收件人")
    addr = models.CharField(max_length=256, verbose_name="地址")
    zip_code = models.CharField(max_length=6, null=True, verbose_name="邮编")
    phone = models.CharField(max_length=11, verbose_name="手机")
    is_default = models.BooleanField(default=False, verbose_name="是否默认地址")

    # 自定义一个模型管理器对象
    objects = AddressManager()

    class Meta:
        db_table = "df_address"
        verbose_name = "地址"
        verbose_name_plural = verbose_name
