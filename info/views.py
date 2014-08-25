# coding:utf-8

# Create your views here.
from info.models import *
from info.form import SearchForm
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.cache import cache
from haystack.views import SearchView
import datetime



PAGE_SIZE = 10
CACHE_PREFIX = 'local_'
CLASS_CACHE_KEY = 'local_class'
AREA_CACHE_KEY = 'local_area'
CACHE_TIME = 60 * 60

def index(request):
    return list(request, 1)

def list(request, page_num):
    all_list = Info.objects.order_by('-pub_date')
    return render_with_list(request, all_list,
                            page_num=page_num,
                            url_name='info.list',)

def query_by_area(request, area_id, page_num):
    all_list = Info.objects.filter(info_area__pk=area_id).order_by('-pub_date')
    return render_with_list(request, all_list,
                            page_num=page_num,
                            url_name='info.by_area',
                            query_id=area_id,)

def query_by_class(request, class_id, page_num):
    all_list = Info.objects.filter(info_class__pk=class_id).order_by('-pub_date')
    return render_with_list(request, all_list,
                            page_num=page_num,
                            url_name='info.by_class',
                            query_id=class_id,)

'''
公用分页方法
'''
def render_with_list(request, all_list, **args):

    fav_list = filter_fav_list(all_list, request.user)
    hot_list = all_list.order_by('-view_times')[:10]

    paginator = Paginator(all_list, PAGE_SIZE)
    page_num = args['page_num']
    page_num = int(page_num)

    context = {
        'paginator' : paginator,
        'page' : paginator.page(page_num),
        'url_name' : args['url_name'],
        'query_id' : args.get('query_id'),
        'hot_list' : hot_list,
        'fav_list' : fav_list,
        'form' : SearchForm()
    }

    return render(request, 'info/list.html', context)

'''
从all_list过滤出fav_list
'''
def filter_fav_list(all_list, user):
    if not user or not user.is_authenticated():
        return None
    try:
        favourite = Favourite.objects.get(user=user)
    except Favourite.DoesNotExist:
        return None

    return all_list.filter(favourite=favourite)

'''
添加到收藏夹
'''
@login_required
def add_favourite(request, id, from_url):
    info = Info.objects.get(pk=id)
    user = request.user
    try:
        favourite = Favourite.objects.get(user=user)
    except Favourite.DoesNotExist:
        favourite = Favourite()
        favourite.user = user
        favourite.save()

    # update or create
    try:
        favouriteInfo = FavouriteInfo.objects.get(favourite=favourite, info=info)
    except:
        favouriteInfo = FavouriteInfo()
        favouriteInfo.favourite = favourite
        favouriteInfo.info = info

    favouriteInfo.add_date = datetime.datetime.now()
    favouriteInfo.save()

    return redirect(from_url)

'''
收藏夹列表
'''
@login_required
def favourite_list(request, page_num):
    user = request.user
    try:
        favourite = Favourite.objects.get(user=user)
    except Favourite.DoesNotExist:
        favourite = Favourite()
        favourite.user = user
        favourite.save()

    fav_list = favourite.infos.all()

    paginator = Paginator(fav_list, PAGE_SIZE)
    page_num = int(page_num)

    context = {
        'paginator' : paginator,
        'page' : paginator.page(page_num),
        'fav_list' : fav_list ,
    }

    return render(request, 'info/fav_list.html', context)


'''
删除收藏
'''
@login_required
def rm_favourite(request, id, from_url):
    info = Info.objects.get(pk=id)
    user = request.user
    try:
        favourite = Favourite.objects.get(user=user)
    except Favourite.DoesNotExist:
        favourite = Favourite()
        favourite.user = user
        favourite.save()

    # update or create
    try:
        favouriteInfo = FavouriteInfo.objects.get(favourite=favourite, info=info)
    except:
        pass
    favouriteInfo.delete()

    return redirect(from_url)

'''
获取收藏
'''
'''
删除收藏
'''
@login_required
def get_favourite(request, info):
    user = request.user
    try:
        favourite = Favourite.objects.get(user=user)
    except Favourite.DoesNotExist:
        return None

    try:
        favouriteInfo = FavouriteInfo.objects.get(favourite=favourite, info=info)
    except:
        return None

    return favouriteInfo

@login_required
def detail(request, id, from_url):
    info = Info.objects.get(pk=id)
    favouriteInfo = get_favourite(request, info)

    # update view times
    info.view_times += 1
    info.save()

    area_num, class_num = get_from_cache(info)

    context = {
        'info': info,
        'from_url': from_url,
        'area_num': area_num,
        'class_num': class_num,
        'favouriteInfo': favouriteInfo
    }

    return render(request, 'info/detail.html', context)


'''
search view
'''
class InfoSearchView(SearchView):

    def create_response(self):

        self.results_per_page = PAGE_SIZE

        """
        Generates the actual HttpResponse to send back to the user.
        """
        (paginator, page) = self.build_page()

        context = {
            'query': self.query,
            'form': self.form,
            'page': page,
            'paginator': paginator,
            'suggestion': None,
        }

        if self.results and hasattr(self.results, 'query') and self.results.query.backend.include_spelling:
            context['suggestion'] = self.form.get_suggestion()

        context.update(self.extra_context())
        return render(self.request, self.template, context)


'''
request processors that return dictionaries to be merged into a
template context

add class and area list to template context
'''
def append_info(request):
    area_list = cache.get(AREA_CACHE_KEY)
    if not area_list:
        area_list = InfoArea.objects.all()
        cache.set(AREA_CACHE_KEY, area_list, CACHE_TIME)
        
    class_list = cache.get(CLASS_CACHE_KEY)
    if not class_list:
        class_list = InfoClass.objects.all()
        cache.set(CLASS_CACHE_KEY, class_list, CACHE_TIME)

    return {"area_list" : area_list, "class_list" : class_list}


'''
缓存每个area和class对应的info数目
'''
def get_from_cache(info):
    key = CACHE_PREFIX + str(info.pk)
    tuple = cache.get(key)
    if not tuple:
        tuple = (info.info_area.info_set.count(),
                 info.info_class.info_set.count())
        cache.set(key, tuple, CACHE_TIME)
    return tuple
