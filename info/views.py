# Create your views here.
from info.models import Info
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

PAGE_SIZE = 4

@login_required
def index(request):
    return list(request, 1)

@login_required
def list(request, pageNum):
    all_list = Info.objects.order_by('-pub_date')
    paginator = Paginator(all_list, PAGE_SIZE)

    pageNum = int(pageNum)

    try:
        info_list = paginator.page(pageNum)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        info_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        info_list = paginator.page(paginator.num_pages)

    prev_page = pageNum - 1 if pageNum > 1 else pageNum
    next_page = pageNum + 1 if pageNum < paginator.num_pages else pageNum

    return render(request, 'info/list.html',
                  {'info_list' : info_list,
                   'page_range' : paginator.page_range,
                   'prev_page' : prev_page,
                   'next_page' : next_page,
                   'curr_page' : pageNum,
                   })

@login_required
def detail(request, id):
    info = Info.objects.get(pk=id);
    return render(request, 'info/detail.html', {'info':info})
