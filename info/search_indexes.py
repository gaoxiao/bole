'''
Created on 2014-8-12

@author: gaoxiao
'''
import datetime
from haystack import indexes
from info.models import Info


class InfoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    author = indexes.CharField(model_attr='title')
    pub_date = indexes.DateTimeField(model_attr='pub_date')

    def get_model(self):
        return Info

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(pub_date__lte=datetime.datetime.now())
