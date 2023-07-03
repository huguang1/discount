from django import template
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db import models, transaction
from django.forms.models import modelform_factory
from django.forms import Media
from django.http import Http404, HttpResponse
from django.utils.encoding import force_text, smart_text
from django.utils.html import escape, conditional_escape
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from xadmin.plugins.ajax import JsonErrorDict
from xadmin.sites import site
from xadmin.util import lookup_field, display_for_field, label_for_field, unquote, boolean_icon
from xadmin.views import BaseAdminPlugin, ModelFormAdminView, ListAdminView
from xadmin.views.base import csrf_protect_m, filter_hook
from xadmin.views.edit import ModelFormAdminUtil
from xadmin.views.list import EMPTY_CHANGELIST_VALUE
from xadmin.layout import FormHelper
from datetime import datetime
from rebate.models import Rec, Site, Items
from django.db.models import Q


class EditablePlugin(BaseAdminPlugin):

    list_editable = []

    def __init__(self, admin_view):
        super(EditablePlugin, self).__init__(admin_view)
        self.editable_need_fields = {}

    def init_request(self, *args, **kwargs):
        active = bool(self.request.method == 'GET' and self.admin_view.has_change_permission() and self.list_editable)
        if active:
            self.model_form = self.get_model_view(ModelFormAdminUtil, self.model).form_obj
        return active

    def result_item(self, item, obj, field_name, row):
        if self.list_editable and item.field and item.field.editable and (field_name in self.list_editable):
            pk = getattr(obj, obj._meta.pk.attname)
            field_label = label_for_field(field_name, obj,
                                          model_admin=self.admin_view,
                                          return_attr=False
                                          )

            item.wraps.insert(0, '<span class="editable-field">%s</span>')
            item.btns.append((
                '<a class="editable-handler" title="%s" data-editable-field="%s" data-editable-loadurl="%s">' +
                '<i class="fa fa-edit"></i></a>') %
                (_(u"Enter %s") % field_label, field_name, self.admin_view.model_admin_url('patch', pk) + '?fields=' + field_name))

            if field_name not in self.editable_need_fields:
                self.editable_need_fields[field_name] = item.field
        return item

    # Media
    def get_media(self, media):
        if self.editable_need_fields:

            try:
                m = self.model_form.media
            except:
                m = Media()
            media = media + m +\
                self.vendor(
                    'xadmin.plugin.editable.js', 'xadmin.widget.editable.css')
        return media


class EditPatchView(ModelFormAdminView, ListAdminView):

    def init_request(self, object_id, *args, **kwargs):
        self.org_obj = self.get_object(unquote(object_id))

        # For list view get new field display html
        self.pk_attname = self.opts.pk.attname

        if not self.has_change_permission(self.org_obj):
            raise PermissionDenied

        if self.org_obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') %
                          {'name': force_text(self.opts.verbose_name), 'key': escape(object_id)})

    def get_new_field_html(self, f):
        result = self.result_item(self.org_obj, f, {'is_display_first':
                                                    False, 'object': self.org_obj})
        return mark_safe(result.text) if result.allow_tags else conditional_escape(result.text)

    def _get_new_field_html(self, field_name):
        try:
            f, attr, value = lookup_field(field_name, self.org_obj, self)
        except (AttributeError, ObjectDoesNotExist):
            return EMPTY_CHANGELIST_VALUE
        else:
            allow_tags = False
            if f is None:
                allow_tags = getattr(attr, 'allow_tags', False)
                boolean = getattr(attr, 'boolean', False)
                if boolean:
                    allow_tags = True
                    text = boolean_icon(value)
                else:
                    text = smart_text(value)
            else:
                if isinstance(f.rel, models.ManyToOneRel):
                    field_val = getattr(self.org_obj, f.name)
                    if field_val is None:
                        text = EMPTY_CHANGELIST_VALUE
                    else:
                        text = field_val
                else:
                    text = display_for_field(value, f)
            return mark_safe(text) if allow_tags else conditional_escape(text)

    @filter_hook
    def get(self, request, object_id):
        model_fields = [f.name for f in self.opts.fields]
        fields = [f for f in request.GET['fields'].split(',') if f in model_fields]
        defaults = {
            "form": self.form,
            "fields": fields,
            "formfield_callback": self.formfield_for_dbfield,
        }
        form_class = modelform_factory(self.model, **defaults)
        form = form_class(instance=self.org_obj)
#         if fields[0] == 'who' and (not self.user.is_superuser):
#             data = '<form method="post" action="/rebate/admin/rebate/recnew/%d/patch/">\
# <div id="div_id_who" class="form-group"> <label for="id_who" class="control-label ">操作人\
# </label> <div class="controls "> <a href="/rebate/admin/rebate/site/add/" title="创建新的 系统管理" class="btn btn-primary btn-sm btn-ajax pull-right" data-for-id="id_who" data-refresh-url="/rebate/admin/rebate/recnew/add/?_field=who&who="><i class="fa fa-plus"></i></a><div class="control-wrap" id="id_who_wrap_container"><select name="who" class="adminselectwidget form-control" id="id_who"><option value="%d">%s</option> \
# </select></div> </div> </div><button type="submit" class="btn btn-success btn-block btn-sm">应用</button></form>' % (int(object_id), self.user.id,self.user.username)
#             return HttpResponse(data)
        if fields[0] == 'who':
            users = Rec.objects.get(id=object_id).activity.site_set.all()
            if not self.user.is_superuser :
                if self.user in users:
                    users = Site.objects.filter(username=self.user.username)
                else:
                    users = Site.objects.filter(username='woqudqbugbug')
            form.fields['who'].queryset = users
        if fields[0] == 'verify':
            if form.initial['verify'] == 1 and (not self.user.is_superuser):
                form.fields['verify'].choices = [(2, '已派发'), (3, '未通过')]
            else:
                form.fields['verify'].choices = [(0, '待处理'), (1, '审核中'), (2, '已派发'), (3, '未通过')]
        helper = FormHelper()
        helper.form_tag = False
        helper.include_media = False
        form.helper = helper

        s = '{% load i18n crispy_forms_tags %}<form method="post" action="{{action_url}}">{% crispy form %}' + \
            '<button type="submit" class="btn btn-success btn-block btn-sm">{% trans "Apply" %}</button></form>'
        t = template.Template(s)
        c = template.Context({'form': form, 'action_url': self.model_admin_url('patch', self.org_obj.pk)})

        return HttpResponse(t.render(c))

    @filter_hook
    @csrf_protect_m
    @transaction.atomic
    def post(self, request, object_id):
        model_fields = [f.name for f in self.opts.fields]
        post_keys = request.POST.keys()
        if 'verify_time_1' in post_keys:
            timestr = request.POST['verify_time_0'] +' '+request.POST['verify_time_1']
            _mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['verify_time'] = datetime.strptime(timestr, "%Y/%m/%d %H:%M")
            request.POST._mutable = _mutable
        if 'start_time_1' in post_keys:
            timestr = request.POST['start_time_0'] +' '+request.POST['start_time_1']
            _mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['start_time'] = datetime.strptime(timestr, "%Y/%m/%d %H:%M")
            request.POST._mutable = _mutable
        if 'end_time_1' in post_keys:
            timestr = request.POST['end_time_0'] +' '+request.POST['end_time_1']
            _mutable = request.POST._mutable
            request.POST._mutable = True
            request.POST['end_time'] = datetime.strptime(timestr, "%Y/%m/%d %H:%M")
            request.POST._mutable = _mutable
        fields = [f for f in request.POST.keys() if f in model_fields]
        defaults = {
            "form": self.form,
            "fields": fields,
            "formfield_callback": self.formfield_for_dbfield,
        }
        form_class = modelform_factory(self.model, **defaults)
        form = form_class(
            instance=self.org_obj, data=request.POST, files=request.FILES)

        result = {}
        if form.is_valid():
            form.save(commit=True)
            result['result'] = 'success'
            result['new_data'] = form.cleaned_data
            result['new_html'] = dict(
                [(f, self.get_new_field_html(f)) for f in fields])
        else:
            result['result'] = 'error'
            result['errors'] = JsonErrorDict(form.errors, form).as_json()
        if 'who' in post_keys:
            Rec.objects.filter(id=int(object_id)).update(verify=1)

        return self.render_response(result)



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

from xadmin.views.base import CommAdminView
from rebate.models import RecMine
class InfoView(CommAdminView):
    # base_template = 'xadmin/base_site.html'
    @csrf_protect_m
    def get(self, request, *args, **kwargs):
        pid = request.GET['pk']
        rec = RecMine.objects.get(id=pid)
        data = '<table class="admin_table"><tbody><tr>'
        infolist = rec.info_post.split('+')
        for info in infolist:
            if info != '':
                item = info.split('◆')
                data += ('<td>' + item[0] + '</td><td>&nbsp;' + item[1] + '</td></tr>')
        data += '</tbody></table>'
        return HttpResponse(data)


# http://127.0.0.1:8000/rebate/admin/rebate/recmine/detail2?pk=2
site.register_plugin(CustomDetailPlugin, ListAdminView)
site.register_view(r'rebate/recmine/detail2', InfoView, name='cp_detail')
site.register_view(r'rebate/recnew/detail2', InfoView, name='cp_detail')
site.register_view(r'rebate/recpass/detail2', InfoView, name='cp_detail')
site.register_plugin(EditablePlugin, ListAdminView)
site.register_modelview(r'^(.+)/patch/$', EditPatchView, name='%s_%s_patch')
