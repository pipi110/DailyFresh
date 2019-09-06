from  django.db import models


class BaseModel(models.Model):
    """模型抽象吉类"""
    create_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now_add=True,verbose_name="创建时间")
    id_delete = models.BooleanField(default=False,verbose_name="逻辑删除")

    class Meta:
        """说明是一个模型基类"""
        abstract = True
