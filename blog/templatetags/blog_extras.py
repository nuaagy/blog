from django import template
from django.db.models import Count

from blog.models import User, Category, Article, Tag

register = template.Library()


@register.inclusion_tag('leftside.html')
def get_query_data(username):
	# 查询当前站点用户对象
	user = User.objects.filter(username=username).first()
	# 查询当前站点对象
	blog = user.blog
	# 当前用户所有文章
	# articles = Article.objects.filter(user__username=username)
	# articles = Article.objects.filter(user=user.id).order_by('-create_time')
	# 查询所有分类及分类下文章数
	category_articles_qs = Category.objects.filter(blog=blog) \
	    .annotate(count=Count('article__category')).values_list('title', 'count')

	# 查询所有标签以及标签下的文章数
	# tag_articles_qs = Tag.objects.filter(blog=blog). \
	# 	annotate(count=Count('article__tag')).values_list('title', 'count')

	tag_articles_qs = Tag.objects.filter(blog=blog). \
		annotate(count=Count('article__tag')).values_list('title', 'count')

	year_month_archive = Article.objects.filter(user=user) \
		.extra(select={'archive': "strftime('%%Y/%%m', create_time)"}) \
		.values('archive').annotate(count=Count('title')) \
		.values_list('archive', 'count')

	print(tag_articles_qs)
	return {'username': username, 'blog': blog, 'categories': category_articles_qs,
			'tags': tag_articles_qs, 'archive': year_month_archive}
