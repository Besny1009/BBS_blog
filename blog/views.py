from django.shortcuts import render, HttpResponse, redirect
from django.http import JsonResponse
from blog.Myform import *
from blog.ultils.validcode import get_valid_code_img
from django.contrib import auth
from blog.models import *
from django.core.paginator import PageNotAnInteger, Paginator, EmptyPage
from django.db.models import F
import json
from django.db import transaction
from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup
import os
from bbs import settings
# Create your views here.

def register(request):
    """
    注册
    :param request:
    :return:
    """
    if request.is_ajax():
        form = UserForm(request.POST)
        # print(form)
        response = {'user': None, 'msg': None}
        if form.is_valid():
            response['user'] = form.cleaned_data.get('user')
            # 生成一条新纪录
            user = form.cleaned_data.get('user')
            pwd = form.cleaned_data.get('pwd')

            email = form.cleaned_data.get('email')
            avatar_obj = request.FILES.get('avatar')
            extar = {}
            if avatar_obj:
                extar['avatar'] = avatar_obj
            UserInfo.objects.create_user(username=user, password=pwd, email=email, **extar)
        else:
            response['msg'] = form.errors
        return JsonResponse(response)
    form_data = UserForm
    return render(request, 'register.html', {'from': form_data})
def get_validCode_img(request):
    """
    获取验证码
    :param request:
    :return:
    """
    data = get_valid_code_img(request)
    return HttpResponse(data)
def login(request):
    """
    登录
    :param request:
    :return:
    """
    if request.method == 'POST':
        response = {'user': None, 'msg': None}
        input_user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        valid_code = request.POST.get('valid_code')
        valid_code_str = request.session.get('valid_code_str')

        if valid_code.upper() == valid_code_str.upper():
               user = auth.authenticate(username=input_user, password=pwd)
               if user:
                   auth.login(request, user)
                   response['user'] = user.username
               else:
                   response['msg'] = "用户名或者密码错误"

        else:
            response['msg'] = "验证码错误"

        return JsonResponse(response)

    return render(request, 'login.html')
def logout(request):
    """
    退出
    :param request:
    :return:
    """
    auth.logout(request)
    return redirect('/login/')
def my_paginator(request, article_list):
    paginator = Paginator(article_list, 15)
    page = request.GET.get('page', 1)
    currentPage = int(page)
    # 如果页数十分多时，换成另外一种方式
    if paginator.num_pages > 11:
        if currentPage - 5 < 11:
            pageRange = range(1, 11)
        elif currentPage + 5 > paginator.num_pages:
            pageRange = range(currentPage - 5, paginator.num_pages + 1)
        else:
            pageRange = range(currentPage - 5, currentPage + 5)
    else:
        pageRange = paginator.page_range
    try:
        article_list = paginator.page(page)
    except PageNotAnInteger:
        article_list = paginator.page(1)
    except EmptyPage:
        article_list = paginator.page(paginator.num_pages)
    return pageRange, paginator, article_list

def index(request):
    """
    首页
    :param request:
    :return:
    """
    article_list = Article.objects.order_by('pk').all().reverse()
    top_up = Article.objects.order_by('up_count').all().reverse()
    pageRange, paginator, article_list = my_paginator(request, article_list)
    return render(request, "index.html", {'article_list': article_list, 'top_up': top_up, 'paginator': paginator, 'pageRange': pageRange})
def home_site(request, username, **kwargs):
    """
    博客首页
    :param request:
    :param username:
    :param kwargs:
    :return:
    """
    user = UserInfo.objects.filter(username=username).first()
    username = user.username
    if not user:
        return render(request, 'not_found.html')
    blog = user.blog
    article_list = Article.objects.filter(user=user)
    right_list = Article.objects.filter(user=user).values("category__name")
    if kwargs:
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        if condition == 'category':
            article_list = article_list.filter(category__name=param)
        elif condition == 'tag':
            article_list = article_list.filter(tag__name=param)
        else:
            year, month = param.split("/")
            article_list = article_list.filter(create_time__year=year, create_time__month=month)
    pageRange, paginator, article_list = my_paginator(request, article_list)

    return render(request, 'home_site.html', locals())

def article_detail(request, username, article_id):
    """
    文章详情
    :param request:
    :param username:
    :param article_id:
    :return:
    """
    user = UserInfo.objects.filter(username=username).first()
    username = user.username
    blog = user.blog
    article_obj = Article.objects.filter(pk=article_id).first()
    comment_list = Comment.objects.filter(article_id=article_id)

    return render(request, 'article_detail.html', locals())

def digg(request):
    """
    点赞功能
    :param request:
    :return:
    """
    article_id = request.POST.get('article_id')
    is_up = json.loads(request.POST.get('is_up'))
    user_id = request.user.pk
    response = {'status': True}
    obj = ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
    if not obj:
        ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)

        article_obj = Article.objects.filter(pk=article_id)

        if is_up:
            article_obj.update(up_count=F("up_count") + 1)
        else:
            article_obj.update(down_count=F("down_count") + 1)
    else:
        response['status'] = False
        response['handled'] = obj.is_up

    return JsonResponse(response)

def comment(request):
    """
    评论功能
    :param request:
    :return:
    """
    article_id = request.POST.get("article_id")
    content = request.POST.get("content")
    pid = request.POST.get("pid")
    user_id = request.user.pk
    article_obj = Article.objects.get(pk=article_id)
    with transaction.atomic():

        comment_obj = Comment.objects.create(user_id=user_id, article_id=article_id, content=content, parent_comment_id=pid)
        Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)
    response = {}
    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d %X")
    response["username"] = request.user.username
    response["content"] = content
    response["parent_con"] = ""
    response["parent_user"] = ""

    if pid:
        response["parent_con"] = comment_obj.parent_comment.content
        response["parent_user"] = comment_obj.parent_comment.user.username

    from django.core.mail import send_mail
    from bbs import settings
    import threading
    t = threading.Thread(target=send_mail, args=("您的文章%s新增了一条评论" % article_obj.title,
                                                     content, settings.EMAIL_HOST_USER, ['15670501272@163.com']))
    t.start()

    return JsonResponse(response)

def get_comment_tree(request):
    """
    获取评论数
    :param request:
    :return:
    """
    article_id = request.GET.get("article_id")
    response = list(Comment.objects.filter(article_id=article_id).order_by('pk').values("pk", "content", "parent_comment_id"))
    return JsonResponse(response, safe=False)

# 后台管理
@login_required
def cn_backend(request):
    """
    后台管理首页
    :param request:
    :return:
    """
    article_list = Article.objects.order_by("-create_time").filter(user=request.user)

    return render(request, 'backend/backend.html', locals())
@login_required
def add_article(request):
    """
    添加文章
    :param request:
    :return:
    """
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        # 防止xss攻击，过滤script标签
        soup = BeautifulSoup(content, 'html.parser')
        for tag in soup.find_all():
            if tag.name == 'script':
                tag.decompose()
        # 构建摘要数据，获取标签字符串的文本前150个字符
        desc = soup.text[0:150] + "..."
        Article.objects.create(title=title, desc=desc, content=content, user=request.user)
        return redirect('/cn_backend/')

    return render(request, 'backend/add_article.html')
def upload(request):
    """
    编译器上传文字图片
    :param request:
    :return:
    """
    img_obj = request.FILES.get('upload_img', None)
    path = os.path.join(settings.MEDIA_ROOT, "add_article_img")

    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, img_obj.name)
    with open(path, "wb") as f:
        if img_obj.multiple_chunks() == False:
            f.write(img_obj.file.read())
        else:
            for line in img_obj.chunks():
                f.write(line)
    response = {
        'error': 0,
        "url": '/media/add_article_img/%s' % img_obj.name
    }
    return HttpResponse(json.dumps(response), content_type="application/json")

def edit_article(request, article_id):
    """
    编辑文章
    :param request:
    :return:
    """
    article_obj = Article.objects.filter(pk=article_id).first()
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        soup = BeautifulSoup(content, 'html.parser')
        for tag in soup.find_all():
            if tag == 'script':
                tag.decompose()

        desc = soup.text[0:150] + '...'
        Article.objects.filter(pk=article_id).update(title=title, desc=desc, content=content, user=request.user)
        return redirect('/cn_backend')
    return render(request, 'backend/edit_article.html', locals())

def delete_article(request, article_id):
    """
    删除文章
    :param request:
    :return:
    """
    Article.objects.filter(pk=article_id).delete()
    return redirect('/cn_backend/')
