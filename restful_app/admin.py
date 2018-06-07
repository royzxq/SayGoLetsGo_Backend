# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.
from django.conf import settings

#
# class AbstractUserAdmin(BaseUserAdmin):
#     form = RegisterForm
#     add_form = RegisterForm
#     list_display = ('username', 'firstname', 'lastname', 'email', 'birth', 'gender', 'password',)
#     fieldsets = (
#         (None, {'fields': ('username', 'email', 'password', 'firstname', 'lastname', 'birth', 'gender', )}),
#         ('Personal info', {'fields': ()}),
#     )
#     list_filter = ('username',)
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'firstname', 'lastname', 'birth', 'email', 'gender', 'password1', 'password2')}
#         ),
#     )
#     filter_horizontal = ()
#     ordering = ('username', 'email', )

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'web_users'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Place)
admin.site.register(Activity)
admin.site.register(Expense)
admin.site.register(TravelGroup)
admin.site.register(Friendship)
admin.site.register(Message)
admin.site.register(Notification)
# admin.site.register(AbstractUser, AbstractUserAdmin)
