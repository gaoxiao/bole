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
CATEGORY_CACHE_KEY = 'local_category'
LOCATION_CACHE_KEY = 'local_location'
NATURE_CACHE_KEY = 'local_nature'
CACHE_TIME = 60 * 60


def index(request):
    return list(request, "", 1)


def parse_para(para_str):
    paraMap = {}
    if para_str and len(para_str) > 0:
        paras = para_str.split(";")
        for p in paras:
            k, v = p.split(",")
            paraMap[k] = v
    return paraMap


def list(request, para, page_num):
    if not para:
        para = ""
    paraMap = parse_para(para)
    location_id = paraMap.get('l_id')
    category_id = paraMap.get('c_id')
    nature_id = paraMap.get('n_id')

    all_list = Info.objects.order_by('-pub_date')
    if location_id:
        all_list = all_list.filter(work_location__pk=location_id)
    if category_id:
        all_list = all_list.filter(work_category__pk=category_id)
    if nature_id:
        all_list = all_list.filter(work_nature__pk=nature_id)

    return render_with_list(request, all_list,
                            page_num=page_num,
                            url_name='info.list',
                            para=para)


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
        'url_name': args.get('url_name'),
        'query_id': args.get('query_id'),
        'para': args.get('para'),
        'hot_list': hot_list,
        'fav_list': fav_list,
        'form': SearchForm(),
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

    context = {
        'info': info,
        'from_url': from_url,
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

    add location , nature and category list to template context
    '''
    location_list = cache.get(LOCATION_CACHE_KEY)
    if not location_list:
        location_list = WorkLocation.objects.all()
        cache.set(LOCATION_CACHE_KEY, location_list, CACHE_TIME)

    nature_list = cache.get(NATURE_CACHE_KEY)
    if not nature_list:
        nature_list = WorkNature.objects.all()
        cache.set(NATURE_CACHE_KEY, nature_list, CACHE_TIME)

    category_map = cache.get(CATEGORY_CACHE_KEY)
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

        cache.set(CATEGORY_CACHE_KEY, category_map, CACHE_TIME)

    return {"location_list": location_list, "category_map": category_map, "nature_list": nature_list}


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
