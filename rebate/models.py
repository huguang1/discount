from django.db import models
from django.contrib.auth.models import AbstractUser
from DjangoUeditor.models import UEditorField
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
# Create your models here.


# 这个类就是活动的详情
class Items(models.Model):
    serial = models.IntegerField('序号', default=0)
    name = models.CharField('活动名称', max_length=100)
    jump_link = models.URLField('外部链接', blank=True)
    detail_link = models.URLField('详情链接', blank=True)
    is_show = models.BooleanField('首页显示', default=True)
    is_active = models.BooleanField('活动开启', default=True)
    ipc = models.BooleanField('IP限制', default=True)
    once_odn = models.BooleanField('单号唯一', default=False)
    verifyc = models.BooleanField('审核时无法申请', default=True)
    timec = models.BooleanField('时间限制', default=False)
    start_time = models.DateTimeField('开启时间', blank=True, null=True)
    end_time = models.DateTimeField('结束时间', blank=True, null=True)
    dailyc = models.BooleanField('每日限制', default=True)
    c_times = models.IntegerField('限制次数', blank=True, null=True)
    c_msg = models.CharField('限制提醒', default='您已提交过申请，请勿重复',max_length=150)
    pic = models.ImageField('活动图片', upload_to='static/', blank=True)
    info = UEditorField('活动详情', width=1000, height=800, imagePath='ueditor/images/', default='', blank=True)
    is_online = models.BooleanField('开启在线申请', default=True)
    class Meta:
        verbose_name = "优惠活动管理"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class ItemInfo(models.Model):
    way_choices = (
        (1, '文本框输入'),
        (0, '文件上传')
    )
    way = models.SmallIntegerField('信息提交方式', default=1,choices=way_choices)
    text = models.CharField('文字描述', max_length=100)
    for_item = models.ForeignKey(Items, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        verbose_name = "申请信息设置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.text


# 管理员管理的游戏
class Site(AbstractUser):
    game = models.ManyToManyField(Items, verbose_name='所管游戏')

    class Meta:
        verbose_name = "系统管理"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


# 会员申请
class Rec(models.Model):
    status_choices = (
        (0, '待处理'),
        (1, '审核中'),
        (2, '已派发'),
        (3, '未通过')
    )
    name = models.CharField('会员账号', max_length=50)
    ip = models.GenericIPAddressField('IP地址')
    activity = models.ForeignKey(Items, verbose_name='申请活动名称', on_delete=models.PROTECT)
    info_post = models.CharField('查看详细', max_length=150, blank=True)
    apply_time = models.DateTimeField('申请时间/信息')
    verify = models.SmallIntegerField('审核状态', default=0, choices=status_choices)
    verify_time = models.DateTimeField('审核时间', blank=True, null=True)
    given = models.DecimalField('派发金额', max_digits=9, decimal_places=2, blank=True, null=True)
    answer = models.CharField('管理员回复', max_length=200, blank=True)
    who = models.ForeignKey(Site, verbose_name='操作人', on_delete=models.SET_NULL, blank=True, null=True)
    lock = models.BooleanField('锁定', default=False)

    class Meta:
        verbose_name = "申请记录"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


@receiver(post_save, sender=Rec)
def notify_handler(instance, created, **kwargs):
    if created:
        name = instance.name
        info = instance.activity
        channel_layer = get_channel_layer()
        admins = Site.objects.filter(game=info)
        for admin in admins:
            print(admin.username, name)
            async_to_sync(channel_layer.group_send)('user_%s' % admin.username, {"type": "chat.message", "message": {"name": name, "info": info.name}})


class RecNew(Rec):

    class Meta:
        verbose_name = "未处理会员"
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return str(self.id)


class RecMine(Rec):

    class Meta:
        verbose_name = "审核中会员"
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return str(self.id)


class RecPass(Rec):

    class Meta:
        verbose_name = "已处理会员"
        verbose_name_plural = verbose_name
        proxy = True

    def __str__(self):
        return self.name




