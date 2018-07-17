from django.db import models
from django.contrib.auth.models import AbstractUser, AbstractBaseUser


class Blog(models.Model):
	# id = models.CharField(primary_key=True)
	title = models.CharField('个人博客标题', max_length=64)
	site_name = models.CharField('站点名称', max_length=64)
	theme = models.CharField('博客主题', max_length=32)

	def __str__(self):
		return self.title


class User(AbstractUser):  # AUTH_USER_MODEL = 'blog.User'
	id = models.AutoField(primary_key=True)
	telephone = models.CharField(max_length=11, null=True, unique=True)
	avatar = models.FileField(upload_to='avatars/', default='avatars/default.png')  # ?
	create_time = models.DateTimeField(verbose_name='注册时间', auto_now_add=True)  # ?

	blog = models.OneToOneField(Blog, on_delete=models.CASCADE, null=True)

	# def __str__(self):
	# 	return self.username


class Category(models.Model):
	title = models.CharField('分类名称', max_length=32)
	blog = models.ForeignKey(Blog, on_delete=models.CASCADE, verbose_name='所属博客')

	def __str__(self):
		return self.title


class Tag(models.Model):
	title = models.CharField('标签名称', max_length=32)
	blog = models.ForeignKey(Blog, on_delete=models.CASCADE, verbose_name='所属博客')


class Article(models.Model):
	title = models.CharField('文章标题', max_length=64)
	description = models.CharField('文章描述', max_length=255)
	create_time = models.DateTimeField(verbose_name='发布时间', auto_now_add=True)
	content = models.TextField('文章内容')

	comment_count = models.IntegerField(default=0)
	up_count = models.IntegerField(default=0)
	down_count = models.IntegerField(default=0)

	user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='作者')  # 连续跨表查询 未分类文章? 优化

	category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
	tag = models.ManyToManyField(Tag, through='Article2Tag')

	# tag = models.ManyToManyField(Tag, through='Article2Tag')  # 中介模型?

	def __str__(self):
		return self.title


class Article2Tag(models.Model):
	article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='文章')
	tag = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name='标签')

	class Meta:
		unique_together = [
			('article', 'tag'),
		]

	def __str__(self):
		return self.article.title + '---->' + self.tag.title


class ArticleUpDown(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
	article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)
	is_up = models.BooleanField(default=True)


class Comment(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='评论用户')
	article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='评论文章')
	content = models.CharField('评论内容', max_length=255)

	create_time = models.DateTimeField('评论时间', auto_now_add=True)
	parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True)  # 自关联 'Comment'或'self'

	def __str__(self):
		return self.content
