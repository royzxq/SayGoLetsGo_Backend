from django.conf.urls import url

from . import consumer

websocket_urlpatterns = [
    url(r'^ws/chat/(?P<group_id>[^/]+)/$', consumer.ChatConsumer),
    url(r'^ws/user/(?P<user_id>[^/]+)/$', consumer.NotificationConsumer),
]