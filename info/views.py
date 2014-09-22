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
                            url_name='info.list', )


def query_by_location(request, location_id, page_num):
    all_list = Info.objects.filter(work_location__pk=location_id).order_by('-pub_date')
    return render_with_list(request, all_list,
                            page_num=page_num,
                            url_name='info.by_location',
                            query_id=location_id, )


def query_by_category(request, category_id, page_num):
    all_list = Info.objects.filter(work_category__pk=category_id).order_by('-pub_date')
    return render_with_list(request, all_list,
                            page_num=page_num,
                            url_name='info.by_category',
                            query_id=category_id, )


def render_with_list(request, all_list, **args):
    '''
    公用分页方法
    '''
    fav_list = filter_fav_list(all_list, request.user)
    hot_list = all_list.order_by('-view_times')[:10]

    paginator = Paginator(all_list, PAGE_SIZE)
    page_num = args['page_num']
    page_num = int(page_num)

    context = {
        'paginator': paginator,
        'page': paginator.page(page_num),
        'url_name': args['url_name'],
        'query_id': args.get('query_id'),
        'hot_list': hot_list,
        'fav_list': fav_list,
        'form': SearchForm()
    }

    return render(request, 'info/list.html', context)


def filter_fav_list(all_list, user):
    '''
    从all_list过滤出fav_list
    '''
    if not user or not user.is_authenticated():
        return None
    try:
        favourite = Favourite.objects.get(user=user)
    except Favourite.DoesNotExist:
        return None

    return all_list.filter(favourite=favourite)


@login_required
def add_favourite(request, id, from_url):
    '''
    添加到收藏夹
    '''
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


@login_required
def favourite_list(request, page_num):
    '''
    收藏夹列表
    '''
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
        'paginator': paginator,
        'page': paginator.page(page_num),
        'fav_list': fav_list,
    }

    return render(request, 'info/fav_list.html', context)


@login_required
def rm_favourite(request, id, from_url):
    '''
    删除收藏
    '''
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


@login_required
def get_favourite(request, info):
    '''
    获取收藏
    '''
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
    if not from_url.startswith('/'):
        from_url = '/' + from_url
    info = Info.objects.get(pk=id)
    favouriteInfo = get_favourite(request, info)

    # update view times
    info.view_times += 1
    info.save()

    category_num = get_from_cache(info)

    context = {
        'info': info,
        'from_url': from_url,
        'category_num': category_num,
        'favouriteInfo': favouriteInfo
    }

    return render(request, 'info/detail.html', context)


class InfoSearchView(SearchView):
    '''
    search view
    '''

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


def append_info(request):
    '''
    request processors that return dictionaries to be merged into a
    template context

    add location and category list to template context
    '''
    location_list = cache.get(AREA_CACHE_KEY)
    if not location_list:
        location_list = WorkLocation.objects.all()
        cache.set(AREA_CACHE_KEY, location_list, CACHE_TIME)

    category_map = cache.get(CLASS_CACHE_KEY)
    if not category_map:
        all_category = WorkCategory.objects.all()
        category_map = {}
        # first level
        for c in all_category:
            if not c.parent:
                category_map[c] = []
        # second level
        for c in all_category:
            if c.parent:
                category_map[c.parent].append(c)

        cache.set(CLASS_CACHE_KEY, category_map, CACHE_TIME)

    return {"location_list": location_list, "category_map": category_map}


def get_from_cache(info):
    '''
    缓存每个category对应的info数目
    '''
    key = CACHE_PREFIX + str(info.pk)
    val = cache.get(key)
    if not val:
        val = info.work_category.info_set.count()
        cache.set(key, val, CACHE_TIME)
    return val
