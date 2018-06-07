# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, render_to_response
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import list_route, detail_route
from rest_framework import permissions, authentication
from .permissions import IsPost, IsTravelGroupUser, IsTravelGroupCreator, IsTravelGroupManager, IsOwnerOrManagerDelete, IsOwnerOrManagerUpdate, IsManagerUpdate, IsCreatorUpdate
from django.contrib.auth import authenticate, login
from rest_framework.authtoken.models import Token
import datetime
from django.conf import settings
from rest_framework.authtoken.views import ObtainAuthToken
from filters.mixins import FiltersMixin
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

from django.db.models import Q
from rest_framework import status, generics
import datetime

# from rest_framework.decorators import action

# Create your views here.

EXPIRE_MINUTES = getattr(settings, 'REST_FRAMEWORK_TOKEN_EXPIRE_MINUTES', 1)


class ObtainExpiringAuthToken(ObtainAuthToken):
    """Create user token"""
    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        token, created = Token.objects.get_or_create(user=serializer.validated_data['user'])
        timezone = token.created.tzinfo
        now = datetime.datetime.now()
        now = now.replace(tzinfo=timezone)
        expiration = now-datetime.timedelta(minutes=EXPIRE_MINUTES)
        if created or token.created < expiration:
            # Update the created time of the token to keep it valid
            token.delete()
            token = Token.objects.create(user=serializer.validated_data['user'])
            token.created = now
            token.save()
        return Response({'token': token.key})


obtain_expiring_auth_token = ObtainExpiringAuthToken.as_view()

def index(request):
    context = {
        'days': [1, 2, 3],
    }
    return render(request, 'index.html')

def register(request):
    # return render(request, 'views/users/register.html')
    return HttpResponseRedirect('/admin/restful_app/abstractuser/add')


class SessionLoginView(APIView):
    permission_classes = (permissions.AllowAny,)
    def post(self, request, format=None):
        print('request data =', request.data)
        username = request.data['username']
        password = request.data['password']
        print(0, username, password)
        user = authenticate(username=username, password=password)
        print(1)
        if user is not None:
            print(2)
            if user.is_active:
                print(3)
                login(request, user)
                print(4)
                return Response('logged on')
        return Response('fail!')


def update(request):
    return render(request, 'views/users/update.html')


def show(request):
    # return render(request, 'views/users/show.html')
    return HttpResponseRedirect('/admin/restful_app/abstractuser')


def detail(request, id):
    return HttpResponse("THE ID IS %s" % id)


class PlaceViewSet(FiltersMixin, viewsets.ModelViewSet):
    queryset = Place.objects.all()
    serializer_class = PlaceSerializer
    pagination_class = PageNumberPagination
    filter_backends = (filters.OrderingFilter, )
    ordering_fields = ('user', 'country', 'city')
    ordering = ('user', 'country', 'city')

    filter_mappings = {
        'user': 'user',
        'country': 'country',
        'city': 'city',
        'travels': 'travels',
    }

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if self.request.user == instance.user:
            instance.editable = True
        serializer = PlaceDetailSerializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        query_params = self.request.query_params
        url_params = self.kwargs

        queryset_filters = self.get_db_filters(url_params=url_params, query_params=query_params)
        db_filters = queryset_filters['db_filters']
        db_excludes = queryset_filters['db_excludes']

        if not self.request.user.is_anonymous and not query_params.dict():
            queryset = Place.objects.filter(Q(user=self.request.user.id) | Q(is_public=True))
        else:
            queryset = Place.objects.all()
        if('search' in query_params):
            return queryset.filter(name__contains=query_params['search']).exclude(**db_excludes)
        return queryset.filter(**db_filters).exclude(**db_excludes)


class ActivityViewSet(FiltersMixin, viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitySerializer
    permissions_classes = (permissions.IsAuthenticatedOrReadOnly, )
    filter_backends = (filters.OrderingFilter, )
    ordering_fields = ('start_time', 'travel', )
    ordering = ('start_time', 'travel', )

    filter_mappings = {
        'travel': 'travel',
    }

    def create(self, request, *args, **kwargs):
        self.serializer_class = ActivityCreateSerializer
        return viewsets.ModelViewSet.create(self, request,  *args, **kwargs)


class FriendshipViewSet(viewsets.ModelViewSet):
    queryset = Friendship.objects.all()
    serializer_class = FriendSerializer

    def create(self, request, *args, **kwargs):
        self.serializer_class = FriendCreateSerializer
        return viewsets.ModelViewSet.create(self, request, *args, **kwargs)

    def perform_create(self, serializer):
        if not self.request.user.is_anonymous:

            serializer.save(me=self.request.user)
        else:
            serializer.save(me=None)





class TravelGroupViewSet(FiltersMixin, viewsets.ModelViewSet):
    serializer_class = TravelGroupListSerializer # default is to get the list
    filter_backends = (filters.OrderingFilter, )
    ordering_fields = ('is_public', 'title',)
    ordering = ('is_public', 'title', )

    filter_mappings = {
        'title': 'title',
        'is_public': 'is_public',
    }

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = TravelGroupDetailSerializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        self.serializer_class = TravelGroupCreateSerializer
        return viewsets.ModelViewSet.create(self, request,  *args, **kwargs)

    def perform_create(self, serializer):
        if not self.request.user.is_anonymous:
            serializer.save(creator=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        if 'users' in request.data:
            serializer = TravelGroupUpdateSerializer(request.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return viewsets.ModelViewSet.partial_update(self, request, *args, **kwargs )

    def get_queryset(self):
        query_params = self.request.query_params
        url_params = self.kwargs
        queryset_filters = self.get_db_filters(url_params=url_params, query_params=query_params)
        db_filters = queryset_filters['db_filters']
        db_excludes = queryset_filters['db_excludes']

        if not self.request.user.is_anonymous and not query_params.dict():
            queryset = User.objects.get(id=self.request.user.id).travelgroup_set.all()
        else:
            queryset = TravelGroup.objects.all()
        if ('search' in query_params):
            return queryset.filter(title__contains=query_params['search']).exclude(**db_excludes)
        return queryset.filter(**db_filters).exclude(**db_excludes)

    permission_classes = (permissions.AllowAny, )
    # permission_classes = (IsTravelGroupUser, permissions.IsAuthenticatedOrReadOnly, )





class UserViewSet(FiltersMixin, viewsets.ModelViewSet):

    serializer_class = UserListSerializer
    filter_backends = (filters.OrderingFilter, )
    ordering_fields = ( 'username', 'email', )
    ordering = ( 'username', 'email',)
    filter_mappings = {
        # 'user_id': 'user_id',
        'username': 'username',
        'email': 'email',
        'travelgroup': 'travelgroup',
    }
    # permission_classes = (IsPost,)

    def create(self, request, *args, **kwargs):
        self.serializer_class = UserCreateSerializer
        return viewsets.ModelViewSet.create(self, request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = UserSerializer(instance)
        return Response(serializer.data)

    def get_queryset(self):
        query_params = self.request.query_params
        url_params = self.kwargs
        queryset_filters = self.get_db_filters(url_params=url_params, query_params=query_params)
        db_filters = queryset_filters['db_filters']
        db_excludes = queryset_filters['db_excludes']
        queryset = User.objects.all()
        if('search' in query_params):
            return queryset.filter(username__contains=query_params['search']).exclude(**db_excludes)

        return queryset.filter(**db_filters).exclude(**db_excludes)
    permission_classes = (permissions.AllowAny, )


class MembershipViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated, IsTravelGroupUser, IsOwnerOrManagerDelete, IsCreatorUpdate)
    #permission_classes = (permissions.AllowAny,)
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer

    def create(self, request, *args, **kwargs):
        self.serializer_class = MembershipCreateSerializer
        return viewsets.ModelViewSet.create(self, request,  *args, **kwargs)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def create(self, request, *args, **kwargs):
        self.serializer_class = ExpenseCreateUpdateSerializer
        return viewsets.ModelViewSet.create(self, request,  *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self.serializer_class = ExpenseCreateUpdateSerializer
        return viewsets.ModelViewSet.update(self, request, *args, **kwargs)

    def get_queryset(self):
        return Expense.objects.filter(paid_member__user=self.request.user)

    #permission_classes = (permissions.AllowAny, )
    permission_classes = (permissions.IsAuthenticated, IsTravelGroupUser, IsOwnerOrManagerDelete, IsOwnerOrManagerUpdate)


class MessageViewset(FiltersMixin, viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (filters.OrderingFilter, )
    ordering = ( '-created_time',)
    filter_mappings = {
        'travel_group': 'travel_group',
    }

    def get_queryset(self):
        query_params = self.request.query_params
        url_params = self.kwargs
        queryset_filters = self.get_db_filters(url_params=url_params, query_params=query_params)
        db_filters = queryset_filters['db_filters']
        db_excludes = queryset_filters['db_excludes']
        queryset = Message.objects.all()
        if('travel_group' in query_params):
            if 'created_time' in query_params:
                s = query_params['created_time']
                return Message.objects.filter(travel_group=query_params['travel_group'], created_time__lt=s).exclude(**db_excludes)
            return queryset.filter(travel_group=query_params['travel_group']).exclude(**db_excludes)


class NotificationViewset(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        query_params = self.request.query_params
        queryset = Notification.objects.all()
        if 'created_time' in query_params:
            return queryset.filter(target=self.request.user, created_time__lt=query_params['created_time']).order_by('-created_time')
        queryset = Notification.objects.filter(target=self.request.user).order_by('-created_time')
        return queryset

    @detail_route(methods=['patch'])
    def has_read(self, request, pk=None):
        notification = self.get_object()
        if self.request.user != notification.target:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        notification.is_read = True
        notification.save()
        return Response({'status': 'change is_read successfully'})
