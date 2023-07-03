# -*- coding: utf-8 -*-
# 18-8-1 下午2:31
# AUTHOR:June
import xadmin
from xadmin.views import BaseAdminPlugin, ListAdminView
from xadmin.views.edit import ModelFormAdminUtil
from xadmin.util import label_for_field
from django.utils.translation import ugettext as _
from django.http.response import JsonResponse, HttpResponse
from xadmin.sites import site
from xadmin.views.base import CommAdminView,csrf_protect_m
from django.template.response import TemplateResponse
from rebate.models import RecMine


class CustomDetailPlugin(BaseAdminPlugin):
    custom_details = {}

    def __init__(self, admin_view):
        super(CustomDetailPlugin, self).__init__(admin_view)
        self.editable_need_fields = {}

    def init_request(self, *args, **kwargs):
        active = bool(self.request.method == 'GET' and self.admin_view.has_view_permission() and self.custom_details)
        if active:
            self.model_form = self.get_model_view(ModelFormAdminUtil, self.model).form_obj
        return active

    def result_item(self, item, obj, field_name, row):
        if self.custom_details and item.field and (field_name in self.custom_details.keys()):
            pk = getattr(obj, obj._meta.pk.attname)
            field_label = label_for_field(field_name, obj,
                        model_admin=self.admin_view,
                        return_attr=False)

            item.wraps.insert(0, '<span class="editable-field">%s</span>')
            title=self.custom_details.get(field_name,{}).get('title',_(u"Details of %s") % field_label)
            default_load_url=self.admin_view.model_admin_url('patch', pk) + '?fields=' + field_name
            load_url = self.custom_details.get(field_name,{}).get('load_url',default_load_url)
            if load_url!=default_load_url:
                concator='?' if load_url.find('?')==-1 else '&'
                load_url=load_url+concator+'pk='+str(pk)
            item.btns.append((
                '<a class="editable-handler" title="%s" data-editable-field="%s" data-editable-loadurl="%s">'+
                '<i class="fa fa-search"></i></a>') %
                 (title, field_name,load_url) )

            if field_name not in self.editable_need_fields:
                self.editable_need_fields[field_name] = item.field
        return item

    # Media
    def get_media(self, media):
        if self.editable_need_fields:
            media = media + self.model_form.media + \
                self.vendor(
                    'xadmin.plugin.editable.js', 'xadmin.widget.editable.css')
        return media


class InfoView(CommAdminView):
    # base_template = 'xadmin/base_site.html'
    @csrf_protect_m
    def get(self, request, *args, **kwargs):
        pid = request.GET['pk']
        rec = RecMine.objects.get(id=pid)
        return HttpResponse(str(rec.info_post))

site.register_plugin(CustomDetailPlugin, ListAdminView)
site.register_view(r'^rebate/recmine/info/$', InfoView, name='cp_detail')