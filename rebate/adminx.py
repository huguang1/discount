# -*- coding: utf-8 -*-
# 18-7-31 下午1:27
# AUTHOR:June
from extra_apps import xadmin
from rebate.models import Site, Items, RecNew, RecMine, RecPass, ItemInfo
from xadmin import views
from django.db.models import Q
from xadmin.plugins.actions import BaseActionView
from django.contrib.auth.forms import UserCreationForm, UserChangeForm


# 创建xadmin的最基本管理器配置，并与view绑定
class BaseSetting(object):
    # 开启主题功能
    enable_themes = True
    use_bootswatch = True
# 将基本配置管理与view绑定
xadmin.site.register(views.BaseAdminView, BaseSetting)


class Globalsettings(object):

    site_title = '优惠活动后台管理系统'
    site_footer = 'By Office Seven'
    # menu_style = 'accordion'
xadmin.site.register(views.CommAdminView,Globalsettings)


class MyAction(BaseActionView):
    action_name = "site-bind"  #: 相当于这个 Action 的唯一标示, 尽量用比较针对性的名字
    description = u'审核所选的 申请'  #: 描述, 出现在 Action 菜单中, 可以使用 ``%(verbose_name_plural)s`` 代替 Model 的名字.

    model_perm = 'change'  #: 该 Action 所需权限

    def do_action(self, queryset):
        queryset.update(who=self.user, verify=1)


class RecNewAdmin(object):
    list_display = ['name', 'activity', 'apply_time', 'ip', 'skip']
    actions = [MyAction]
    custom_details = {'activity': {'title': u'申请信息', 'load_url': 'detail2'}}
    readonly_fields = ['verify', 'verify_time', 'answer', 'activity', 'info_post', 'name', 'ip', 'given', 'apply_time', 'lock', 'who']
    model_icon = 'fa fa-spinner'
    ordering = ['apply_time']
    refresh_times = (10, 30, 60, 300)

    def queryset(self):
        user = Site.objects.get(username=self.user.username)
        games = user.game.all()
        qs = super(RecNewAdmin, self).queryset()
        qs = qs.exclude(lock=True).filter(verify=0).filter(activity__in=games)
        return qs

    def skip(self, name):
        from django.utils.safestring import mark_safe
        return mark_safe("<a href='/rebate/skip/?name=%s'>锁定</>" % name)
    skip.short_description = '<font color="#428BCA">操作</font>'


class RecMineAdmin(object):
    list_display = ['name', 'activity', 'apply_time', 'answer', 'verify', 'ip', 'given', 'skip']
    custom_details = {'apply_time': {'title': u'申请信息', 'load_url': 'detail2'}}
    list_editable = ['verify', 'answer', 'given']
    search_fields = ['name', 'activity', 'who', 'verify']
    list_filter = ['verify']
    readonly_fields = ['activity', 'info_post', 'name', 'ip', 'apply_time']
    model_icon = 'fa fa-bullseye'
    ordering = ['apply_time']

    def queryset(self):
        user = Site.objects.get(username=self.user.username)
        games = user.game.all()
        qs = super(RecMineAdmin, self).queryset()
        qs = qs.exclude(verify=0).filter(Q(verify=1) | Q(verify_time__isnull=True) | Q(answer__isnull=True) | Q(lock=True)).filter(activity__in=games)
        return qs

    def skip(self, name):
        from django.utils.safestring import mark_safe
        return mark_safe("<a href='/rebate/pass/?name=%s'>释放</>" % name)
    skip.short_description = '<font color="#428BCA">操作</font>'


class RecPassAdmin(object):
    list_display = ['name', 'who', 'activity', 'apply_time', 'verify', 'answer', 'verify_time', 'ip', 'given']
    custom_details = {'apply_time': {'title': u'申请信息', 'load_url': 'detail2'}}
    search_fields = ['name', 'activity', 'who', 'verify']
    list_filter = ['verify_time', 'verify']
    readonly_fields = ['activity', 'info_post', 'answer', 'who', 'name', 'ip', 'apply_time', 'given', 'lock', 'verify', 'verify_time']
    model_icon = 'fa fa-check-square'
    ordering = ['-verify_time']

    def queryset(self):
        user = Site.objects.get(username=self.user.username)
        games = user.game.all()
        qs = super(RecPassAdmin, self).queryset()
        qs = qs.filter(verify_time__isnull=False).filter(answer__isnull=False).filter(Q(verify=2) | Q(verify=3)).filter(lock=False).filter(activity__in=games)
        return qs




class ItemInfoInline(object):
    model = ItemInfo
    extra = 0


class ItemAdmin(object):
    list_display = ['serial', 'name', 'ipc','once_odn', 'is_active', 'is_show']
    inlines = [ItemInfoInline,]
    style_fields = {'info': 'ueditor'}
    list_editable = ['ipc', 'once_odn', 'is_active', 'is_show', 'serial']
    model_icon = 'fa fa-tasks'
    ordering = ['serial']


class XadminUser(UserCreationForm):
    class Meta:
        fields = ("username", "is_staff", "groups", "game")


class SiteAdmin(object):
    list_display = ['username', 'game', 'last_login', 'is_active']
    
    def get_model_form(self, **kwargs):
        if self.org_obj is None:
            self.form = XadminUser
        else:
            self.form = UserChangeForm
        return super(SiteAdmin, self).get_model_form(**kwargs)


xadmin.site.unregister(Site)
xadmin.site.register(RecNew, RecNewAdmin)
xadmin.site.register(RecMine, RecMineAdmin)
xadmin.site.register(RecPass, RecPassAdmin)
xadmin.site.register(Items, ItemAdmin)
xadmin.site.register(Site, SiteAdmin)
xadmin.site.register(ItemInfo)

