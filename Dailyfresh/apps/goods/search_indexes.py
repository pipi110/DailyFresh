from .models import GoodsSKU
from haystack import indexes


class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return GoodsSKU

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        #确定在建立索引时有些记录被索引，这里我们简单地返回所有记录
        return self.get_model().objects.all()
