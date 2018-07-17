"""BBS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path

from blog import views

urlpatterns = [
	path('admin/', admin.site.urls),
	path('login/', views.login, name='login'),
	path('logout/', views.logout, name='logout'),
	path('digg/', views.digg),  # ajax /
	path('code/', views.code),
	path('upload/', views.upload),
	path('comment/', views.comment),
	path('backend/', views.backend),
	path('addarticle/', views.addarticle),
	path('', views.index),
	re_path(r'^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<params>.*)/$', views.homesite,
			name='homesite'),
	re_path(r'^(?P<username>\w+)/$', views.homesite),
	path('<username>/article/<article_id>/', views.article_detail, name='article_detail')
]
