import json
import os

from django.shortcuts import render, redirect, HttpResponse
from django.contrib import auth
from django.db.models import F
from django.db import transaction
from django.http import JsonResponse

from blog.models import Article, User, ArticleUpDown, Comment, Category, Tag, Article2Tag
from BBS.settings import BASE_DIR
from blog.code import check


def login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		check_code_ignore = request.POST.get('code').lower()

		if check_code_ignore != request.session.get('check_code'):
			return render(request, 'login.html', {'msg': '验证码错误'})

		user = auth.authenticate(request, username=username, password=password)
		if user is not None:
			auth.login(request, user)
			return redirect(index)
		else:
			return render(request, 'login.html', {'msg': '用户名或密码错误'})

	return render(request, 'login.html')


def code(request):
	img, check_code = check()
	print(check_code)
	request.session['check_code'] = check_code.lower()
	from io import BytesIO
	stream = BytesIO()
	img.save(stream, 'png')
	return HttpResponse(stream.getvalue())


def index(request):
	articles = Article.objects.all().order_by('-create_time')
	return render(request, 'index.html', {'articles': articles})


def logout(request):
	auth.logout(request)
	return redirect(index)


def homesite(request, username, **kwargs):
	user = User.objects.filter(username=username).first()
	if not user:
		return render(request, 'not_found.html', {'dt': '07/12/2018'})
	blog = user.blog
	if not kwargs:
		articles = Article.objects.filter(user=user).order_by('-create_time')
	else:
		condition = kwargs.get('condition')
		params = kwargs.get('params')
		if condition == 'tag':
			articles = Article.objects.filter(user__username=username, tag__title=params)
		elif condition == 'category':
			articles = Article.objects.filter(user=user, category__title=params)
			# articles = Article.objects.filter(user=user.id, category__title=params)
		else:
			# year, month = params.split('/')
			try:
				year, *_, month = params.partition('/')
				articles = Article.objects. \
					filter(user__username=username, create_time__year=year, create_time__month=month)
			except ValueError:
				articles = Article.objects.filter(user=user).order_by('-create_time')
	return render(request, 'homesite.html', locals())


def article_detail(request, username, article_id):
	user = User.objects.filter(username=username).first()
	blog = user.blog
	detail_article = Article.objects.filter(user__username=username, pk=article_id).first()
	comments = Comment.objects.filter(article_id=article_id)
	return render(request, 'article_detail.html', locals())


def digg(request):
	if request.method == "POST":
		user_id = request.user.pk
		is_up = json.loads(request.POST.get('is_up'))  # 'true'反序列化True
		article_id = request.POST.get('article_id')

		digg_bury_record = ArticleUpDown.objects.filter(article_id=article_id, user_id=user_id).first()

		response = {'status': True}

		if digg_bury_record:  # 当前登录用户是否赞灭过文章
			response['status'] = False
			response['is_up'] = digg_bury_record.is_up
		else:  # 重复赞灭
			# 文章赞灭表
			with transaction.atomic():  # 开启事务，原子性操作
				ArticleUpDown.objects.create(article_id=article_id, user_id=user_id, is_up=is_up)
				# 文章表增加赞灭数，F
				# raise ValueError("66")
				if is_up:
					Article.objects.filter(pk=article_id).update(up_count=F('up_count') + 1)
				else:
					Article.objects.filter(pk=article_id).update(down_count=F('up_count') + 1)
		return JsonResponse(response)
		# HttpResponse  json.dumps()   JSON.parse()
		# {status: false, msg: null, is_up: true}


def comment(request):
	parent_comment_id = request.POST.get('parent_comment_id')
	content = request.POST.get('content')
	user_id = request.user.pk
	article_id = request.POST.get('article_id')
	with transaction.atomic():
		new_comment_record = Comment.objects.create(parent_comment_id=parent_comment_id, content=content,
													user_id=user_id, article_id=article_id)

		Article.objects.filter(pk=article_id).update(comment_count=F('comment_count') + 1)

	response = {'status': True}
	response['time'] = new_comment_record.create_time.strftime('%Y-%m-%d %X')  # datetime对象json无法序列化
	response['content'] = new_comment_record.content  # ? 数据库存储处理

	return JsonResponse(response)


def backend(request):
	if request.user.is_authenticated:
		articles = Article.objects.filter(user=request.user)
		return render(request, 'backend/backend.html', locals())  # request articles
	return redirect(login)


def addarticle(request):
	# if request.user.is_authenticated:
	#     return render(request, 'backend/addarticle.html')
	if request.method == "POST":
		title = request.POST.get('title')
		content = request.POST.get('content')
		category = request.POST.get('category')  # '5'
		tag_list = request.POST.getlist('tag')  # ['1', '2', '3']

		from bs4 import BeautifulSoup
		bs = BeautifulSoup(content, 'html.parser')
		for tag in bs.find_all():
			if tag.name in ['script']:
				tag.decompose()

		content = str(bs)
		desc = bs.text[:150]

		new_article_obj = Article.objects.create(title=title, content=content, description=desc,
												 user=request.user, category_id=category)
		for tag_pk in tag_list:
			Article2Tag.objects.create(article_id=new_article_obj.pk, tag_id=tag_pk)

		return redirect(backend)
	else:
		blog = request.user.blog
		categories = Category.objects.filter(blog=blog)
		tags = Tag.objects.filter(blog=blog)
		return render(request, 'backend/addarticle.html', locals())


def upload(request):
	print(request.FILES)
	img = request.FILES.get('img')
	path = os.path.join(BASE_DIR, 'static/upload', img.name)
	with open(path, 'wb') as fp:
		for line in request.FILES.get('img'):
			fp.write(line)
	# 访问http://127.0.0.1:8888/static/upload/character.png
	response = {
		"error": 0,
		"url": "/static/upload/" + img.name
	}
	return JsonResponse(response)
