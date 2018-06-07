"""SayGoLetsGo_Backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include

from rest_framework import routers
from restful_app.views import index
# from chat.views import index


# router = routers.DefaultRouter()
# router.register(r'test', views.UserViewSet)
# router.register(r'abuser', views.ABUserViewSet)




urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^restful_app/', include('restful_app.urls')),
    url(r'^ws_app/', include('ws_app.urls')),
    url(r'^$', index, name='index'),
    # url(r'^group/$', views.group_list),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
]
