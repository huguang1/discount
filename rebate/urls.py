# -*- coding: utf-8 -*-
# 18-7-31 下午1:58
# AUTHOR:June
from django.conf.urls import url
from rebate.views import IndexView, ItemView, RecView, MineView, QueryView, SkipView, PassView, IndexWapView, RecWapView
app_name = 'rebate'

urlpatterns = [
    url(r'indexwap', IndexWapView.as_view(), name='indexwap'),
    url(r'items', ItemView.as_view(), name='items'),
    url(r'rec$', RecView.as_view(), name='rec'),
    url(r'recwap$', RecWapView.as_view(), name='recwap'),
    url(r'mine', MineView.as_view(), name='mine'),
    url(r'query', QueryView.as_view(), name='query'),
    url(r'^skip$', SkipView.as_view(), name='skip'),
    url(r'^pass/$', PassView.as_view(), name='pass'),
    url(r'', IndexView.as_view(), name='index'),
]

