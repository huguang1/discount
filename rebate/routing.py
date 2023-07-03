from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^rebate/chat/(?P<user_name>[^/]+)/$', consumers.ChatConsumer),
]

