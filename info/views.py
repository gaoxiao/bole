# Create your views here.
from django.http import HttpResponse
from info.models import Info
from django.template import loader
from django.template.context import Context
from django.shortcuts import render

def index(request):
    latest_list = Info.objects.order_by('-pub_date')[:5]
    template = loader.get_template('info/index.html')
    context = {'latest_list': latest_list}
    return render(request, 'info/index.html', context)
