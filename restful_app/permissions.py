from rest_framework import permissions
from .models import *


class IsTravelGroupUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        group = get_travel_group(obj)
        if request.user in group.users.all():
            return True
        return False


class IsTravelGroupCreator(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        group = get_travel_group(obj)
        membership = group.membership_set.get(user=request.user)
        if membership.is_creator is True:
            return True
        return False


class IsTravelGroupManager(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        group = get_travel_group(obj)
        membership = group.membership_set.get(user=request.user)
        if membership.is_creator is True:
            return True
        if membership.is_manager is True:
            return True
        return False


class IsPost(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return True
        return not request.user.is_anonymous


class IsOwnerOrManagerDelete(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method != 'DELETE':
            return True
        group = get_travel_group(obj)
        membership = group.membership_set.get(user=request.user)
        ret = -1
        if membership.is_creator is True:
            ret = 0
        if membership.is_manager is True:
            ret = 0
        if type(obj) is Expense:
            user = obj.paid_member.user
        else:
            user = obj.user
        if user == request.user:
            ret = 0
        if ret == -1:
            return False
        return True


class IsOwnerOrManagerUpdate(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method != 'PUT':
            return True
        group = get_travel_group(obj)
        membership = group.membership_set.get(user=request.user)
        ret = -1
        if membership.is_creator:
            ret = 0
        if membership.is_manager:
            ret = 0
        if type(obj) is Expense:
            user = obj.paid_member.user
        else:
            user = obj.user
        if user == request.user:
            ret = 0
        if ret == -1:
            return False
        return True


class IsManagerUpdate(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method != 'PUT':
            return True
        group = get_travel_group(obj)
        membership = group.membership_set.get(user=request.user)
        ret = -1
        if membership.is_creator:
            ret = 0
        if membership.is_manager:
            ret = 0
        if ret == -1:
            return False
        return True


class IsCreatorUpdate(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method != 'PUT':
            return True
        group = get_travel_group(obj)
        membership = group.membership_set.get(user=request.user)
        return membership.is_creator


class FriendshipPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            if request.user.is_anonymous:
                return False
            else:
                return True
        elif request.method == 'DELETE':
            if request.user == obj.user1 or request.user == obj.user2:
                return True
            return False
        return False
