# Create your views here.
from info.models import Info
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    latest_list = Info.objects.order_by('-pub_date')[:5]
    return render(request, 'info/index.html', {'latest_list': latest_list})

@login_required
def detail(request, id):
    info = Info.objects.get(pk=id);
    return render(request, 'info/detail.html', {'info':info})
