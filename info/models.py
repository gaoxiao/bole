from django.db import models

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
