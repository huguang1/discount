# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from rebate.models import Items, RecNew, RecMine, RecPass, ItemInfo, Rec
from django.views.generic import View
from django.http.response import JsonResponse, HttpResponse
from django.http import HttpResponseRedirect
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.contrib import messages
import datetime
import pytz


class IndexView(View):
    def get(self, request):
        items = Items.objects.filter(is_show=True).order_by('-serial')
        sets = []
        for item in items:
            iteminfos = ItemInfo.objects.filter(for_item=item)
            infostr = []
            for iteminfo in iteminfos:
                infostr.append((iteminfo.text))
            sets.append({
                "Url": item.jump_link,
                "ClassRemark": '../rebate/media/' + str(item.pic),
                "T_ProClassName": item.name,
                "T_ProClassID": item.id,
                "T_ProClassKey": item.info,
                "T_ProClassDes": item.serial,
                "IsXz": '1' if item.ipc else '0',
                "IsBlock": '1' if item.is_show else '0',
                "IsDayXz": '1' if item.dailyc else '0',
                "DayXzMessage": item.c_msg,
                "IsOpen": '1' if item.is_active else '0',
                "IsTimeXz": '1' if item.timec else '0',
                "WapImage": '',
                "DetailUrl": item.detail_link,
                "IsOrderXz": '1' if item.once_odn else '0',
                "IsCheckState": '1' if item.verifyc else '0',
                "InfoList": infostr,
		"jump_link": item.jump_link if item.jump_link else None
            })
        infos = Rec.objects.all().order_by("-id")[0:10]
        for info in infos:
            info.name = info.name[0:1]
        return render(request, 'index.html', {'sets': sets, 'infos': infos})


class IndexWapView(View):
    def get(self, request):
        items = Items.objects.filter(is_show=True).order_by('-serial')
        sets = []
        for item in items:
            iteminfos = ItemInfo.objects.filter(for_item=item)
            infostr = []
            for iteminfo in iteminfos:
                infostr.append((iteminfo.text))
            sets.append({
                "Url": item.jump_link,
                "ClassRemark": '../rebate/media/' + str(item.pic),
                "T_ProClassName": item.name,
                "T_ProClassID": item.id,
                "T_ProClassKey": item.info,
                "T_ProClassDes": item.serial,
                "IsXz": '1' if item.ipc else '0',
                "IsBlock": '1' if item.is_show else '0',
                "IsDayXz": '1' if item.dailyc else '0',
                "DayXzMessage": item.c_msg,
                "IsOpen": '1' if item.is_active else '0',
                "IsTimeXz": '1' if item.timec else '0',
                "WapImage": '',
                "DetailUrl": item.detail_link,
                "IsOrderXz": '1' if item.once_odn else '0',
                "IsCheckState": '1' if item.verifyc else '0',
                "InfoList": infostr,
		"jump_link": item.jump_link if item.jump_link else None
            })
        return render(request, 'indexwap.html', {'sets': sets})


class ItemView(View):
    def post(self, request):
        items = Items.objects.filter(is_show=True).order_by('-serial')
        sets = []
        for item in items:
            iteminfos = ItemInfo.objects.filter(for_item=item)
            infostr = ''
            for iteminfo in iteminfos:
                infostr += (iteminfo.text + '|'+str(iteminfo.way)+',')
            sets.append({
                "Url": item.jump_link,
                "ClassRemark": '../rebate/media/'+str(item.pic),
                "T_ProClassName": item.name,
                "T_ProClassID": item.id,
                "T_ProClassKey": item.info,
                "T_ProClassDes": item.serial,
                "IsXz": '1' if item.ipc else '0',
                "IsBlock": '1' if item.is_show else '0',
                "IsDayXz": '1' if item.dailyc else '0',
                "DayXzMessage": item.c_msg,
                "IsOpen": '1' if item.is_active else '0',
                "IsTimeXz": '1' if item.timec else '0',
                "WapImage": '',
                "DetailUrl": item.detail_link,
                "IsOrderXz": '1' if item.once_odn else '0',
                "IsCheckState": '1' if item.verifyc else '0',
                "InfoList": infostr
            })
        return HttpResponse(str(sets))


class RecView(View):

    def post(self, request):
        act_id = request.GET.get('act_id')
        if 'HTTP_X_FORWARDED_FOR' in request.META.values():
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']

        username = request.POST['str1']
        if not username:
            return render(request, 'alert.html', {'data': "请输入正确会员"})

        # 获取申请的活动信息
        item = Items.objects.get(id=act_id)
        # 无需在线申请
        if not item.is_online:
            return render(request, 'alert.html', {'data': "无需在线申请,系统统一派送"})
        # 活动是否开启
        if not item.is_active:
            return render(request, 'alert.html', {'data': "活动未开启"})
        # ip限制
        if item.ipc:
            recs = Rec.objects.filter(activity=item)
            if recs.exists():
                for rec in recs:
                    if rec.ip == ip:
                        return render(request, 'alert.html', {'data': "该IP已申请,请勿重复提交"})
        # 是否时间正确
        if item.timec:
            now = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone('UTC'))
            if not (item.start_time <= now <= item.end_time):
                return render(request, 'alert.html', {'data': "不是申请时间,详细请点击“查看详细”"})

        # 活动申请每日限制
        if item.dailyc:
            tod = datetime.date.today()
            tom = datetime.date.today() + datetime.timedelta(days=1)
            nums = Rec.objects.filter(name=username).filter(activity=item).filter(apply_time__gte=tod).filter(apply_time__lt=tom).count()
            if nums >= item.c_times:
                return render(request, 'alert.html', {'data': "达到每日提交的上限"})

        # 审核中无法提交
        if item.verifyc:
            recs = Rec.objects.filter(name=username).filter(activity=item).filter(Q(verify=0) | Q(verify=1))
            if recs.exists():
                return render(request, 'alert.html', {'data': "您的申请正在审核中，请勿重复提交....."})
        info = '会员账号: ◆ %s' % username + '+'
        iteminfos = item.iteminfo_set.all()
        i = 1
        for iteminfo in iteminfos:
            info += iteminfo.text + ': ◆ ' +request.POST.get('%s_str_%s' % (act_id, str(i)), '') + '+'
            i += 1
        nowtime = timezone.now()

        try:
            item = Items.objects.filter(id=int(act_id)).first()
            Rec.objects.create(activity=item, name=username, info_post=info, apply_time=nowtime, ip=ip)
        except Exception as e:
            return render(request, 'alert.html', {'data': "提交失败,请联系客服人员"})
        return render(request, 'alert.html', {'data': "提交成功"})


class RecWapView(View):

    def post(self, request):
        act_id = request.GET.get('act_id')
        if 'HTTP_X_FORWARDED_FOR' in request.META.values():
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        username = request.POST['str1']
        if not username:
            return render(request, 'alertwap.html', {'data': "请输入正确会员"})

        # 获取申请的活动信息
        item = Items.objects.get(id=act_id)
        # 无需在线申请
        if not item.is_online:
            return render(request, 'alertwap.html', {'data': "无需在线申请,系统统一派送"})
        # 活动是否开启
        if not item.is_active:
            return render(request, 'alertwap.html', {'data': "活动未开启"})
        # ip限制
        if item.ipc:
            recs = Rec.objects.filter(activity=item)
            if recs.exists():
                for rec in recs:
                    if rec.ip == ip:
                        return render(request, 'alertwap.html', {'data': "该IP已申请,请勿重复提交"})
        # 是否时间正确
        if item.timec:
            now = datetime.datetime.utcnow().replace(tzinfo=pytz.timezone('UTC'))
            if not (item.start_time <= now <= item.end_time):
                return render(request, 'alertwap.html', {'data': "不是申请时间,详细请点击“查看详细”"})

        # 活动申请每日限制
        if item.dailyc:
            tod = datetime.date.today()
            tom = datetime.date.today() + datetime.timedelta(days=1)
            nums = Rec.objects.filter(name=username).filter(activity=item).filter(apply_time__gte=tod).filter(apply_time__lt=tom).count()
            if nums >= item.c_times:
                return render(request, 'alertwap.html', {'data': "达到每日提交的上限"})

        # 审核中无法提交
        if item.verifyc:
            recs = Rec.objects.filter(name=username).filter(activity=item).filter(Q(verify=0) | Q(verify=1))
            if recs.exists():
                return render(request, 'alertwap.html', {'data': "您的申请正在审核中，请勿重复提交....."})

        info = '会员账号: ◆ %s' % username + '+'
        iteminfos = item.iteminfo_set.all()
        i = 1
        for iteminfo in iteminfos:
            info += iteminfo.text + ': ◆ ' + request.POST.get('%s_str_%s' % (act_id, str(i)), '') + '+'
            i += 1

        nowtime = timezone.now()
        try:
            item = Items.objects.filter(id=int(act_id)).first()
            Rec.objects.create(activity=item, name=username, info_post=info, apply_time=nowtime, ip=ip)
        except Exception as e:
            return render(request, 'alertwap.html', {'data': "提交失败,请联系客服人员"})
        return render(request, 'alertwap.html', {'data': "提交成功"})


class MineView(View):
    def post(self, request):
        username = request.POST['user_name']
        act_name = request.POST['act_name']
        item = Items.objects.get(name=act_name)
        recs = Rec.objects.filter(activity=item).filter(name=username).exclude(verify=0)
        if recs.exists():
            data = []
            status_choices = {
                0: '待处理',
                1: '审核中',
                2: '已派发',
                3: '未通过'
            }
            for rec in recs:
                data.append({
                    "T_ProductName": username,
                    "ZsMoney": str(rec.given) if rec.given else '',
                    "T_ProFlag": rec.info_post,
                    "T_DateTime": (rec.apply_time+timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                    "Remark": rec.answer,
                    "T_ProductNote": status_choices[int(rec.verify)],
                })
            return JsonResponse({"count": 3, "data": data})
        else:
            return JsonResponse({"count": 0})


class QueryView(View):
    def post(self, request):
        recs = Rec.objects.filter(verify=2).filter(answer__isnull=False).filter(lock=False).order_by('-verify_time')[0:49]
        data = []
        for rec in recs:
            data.append({
                "T_ProductName": rec.name[0:-3]+'***',
                "T_ProClassName": rec.activity.name,
            })
        return HttpResponse(str(data))


class SkipView(View):
    def get(self, request):
        params = request.GET['name']
        rec_object = Rec.objects.get(id=int(params))
        if not rec_object.lock :
            rec_object.lock = True
            rec_object.verify = 1
            rec_object.save()
            return HttpResponseRedirect('/rebate/admin/rebate/recmine/')
        else:
            messages.add_message(request, messages.WARNING, '该申请已交由他人处理！')
            return redirect('/rebate/admin/rebate/recnew/')


class PassView(View):
    def get(self, request):
        params = request.GET['name']
        rec_object = Rec.objects.get(id=int(params))
        if (rec_object.verify == 2 or rec_object.verify == 3) and rec_object.answer:
            rec_object.lock = False
            rec_object.verify_time = datetime.datetime.now()
            rec_object.who = request.user
            rec_object.save()
            return HttpResponseRedirect('/rebate/admin/rebate/recnew/')
        else:
            messages.add_message(request, messages.WARNING, '请完善相应的处理信息！')
            return redirect('/rebate/admin/rebate/recmine/')

