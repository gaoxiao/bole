from django.db import models

from account.compat import AUTH_USER_MODEL

from account.conf import settings
AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")

# Create your models here.
class InfoArea(models.Model):
    areaName = models.CharField(max_length=100)
    def __unicode__(self):
        return self.areaName

class InfoClass(models.Model):
    className = models.CharField(max_length=100)
    def __unicode__(self):
        return self.className

class Info(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    view_times = models.IntegerField(default=0)
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    info_area = models.ForeignKey(InfoArea)
    info_class = models.ForeignKey(InfoClass)
    def __unicode__(self):
        return self.title
    
class Favourite(models.Model):
    user = models.OneToOneField(AUTH_USER_MODEL, verbose_name="user")
    infos = models.ManyToManyField(Info, through='FavouriteInfo')

class FavouriteInfo(models.Model):
    favourite = models.ForeignKey(Favourite)
    info = models.ForeignKey(Info)
    add_date = models.DateTimeField('info add time', auto_now_add=True)
    
    class Meta:
        unique_together = (('favourite', 'info'))
