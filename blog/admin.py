from django.contrib import admin

from blog import models

# admin.site.register(models.User)
admin.site.register(models.Blog)
admin.site.register(models.Category)
admin.site.register(models.Tag)
admin.site.register(models.Article)
admin.site.register(models.Article2Tag)
admin.site.register(models.ArticleUpDown)
admin.site.register(models.Comment)


class UserAdmin(admin.ModelAdmin):
	list_display = ('username', 'email', 'telephone', 'last_login', 'avatar', 'create_time')

admin.site.register(models.User, UserAdmin)