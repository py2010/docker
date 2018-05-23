# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.forms import widgets

from cmdb import models
from forms import HostForm, BalanceForm, AppForm, A10Form, AppConfForm

from readonly.addreadonly import ReadOnlyAdmin, ReadOnlyEditAdmin, MyAdmin as MyAdmin
from suit import apps
# 表单编辑界面input等默认宽度为col-lg-7，有些窄，改为col-lg-9
apps.DjangoSuitConfig.form_size['default'] = apps.SUIT_FORM_SIZE_XXX_LARGE

# import types
# @classmethod
# def addMethod(cls, func):
#     return setattr(cls, func.__name__, types.MethodType(func, cls))


# from django.contrib import auth
# admin.site.unregister(auth.models.User)


# @admin.register(auth.models.User)
# class MyUserAdmin(auth.admin.UserAdmin):
#     # 自定义auth.User后台版面
#     def __init__(self, model, admin_site):
#         self.suit_form_tabs = [('/tab_1', 'name1'), ('/tab_2', 'name2'), ]
#         super(self.__class__, self).__init__(model, admin_site)


@admin.register(models.Docker)
class Docker_admin(MyAdmin):
    list_display = ('name', 'ip', 'port', 'tls', )
    search_fields = ('ip', 'name')

