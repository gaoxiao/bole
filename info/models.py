from django.db import models

from account.compat import AUTH_USER_MODEL

from account.conf import settings

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")

# Create your models here.
class WorkCategory(models.Model):
    categoryName = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True, blank=True)

    def __unicode__(self):
        return self.categoryName


class WorkLocation(models.Model):
    location = models.CharField(max_length=100)

    def __unicode__(self):
        return self.location


class WorkNature(models.Model):
    nature = models.CharField(max_length=100)

    def __unicode__(self):
        return self.nature


class Info(models.Model):
    title = models.CharField(max_length=200)
    work_experience = models.CharField(max_length=200, blank=True, null=True)
    degree = models.CharField(max_length=200, blank=True, null=True)

    pub_date = models.DateTimeField('date published', auto_now_add=True)
    effective_date = models.DateTimeField('effective date',  blank=True, null=True)
    uneffective_date = models.DateTimeField('uneffective date', blank=True, null=True)

    recruit_number = models.IntegerField(default=0)

    requirement = models.TextField()
    description = models.TextField()
    view_times = models.IntegerField(default=0)

    work_nature = models.ForeignKey(WorkNature)
    work_category = models.ForeignKey(WorkCategory)
    work_location = models.ManyToManyField(WorkLocation, verbose_name="work city")

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
