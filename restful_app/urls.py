from django.urls import path
from . import views, models
from .serializers import NotificationSerializer
from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets
from rest_framework.authtoken import views as rest_framework_views
#from django.views.decorators.csrf import csrf_exempt


# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = User
#
#         fields = ('url', 'username', 'email')
#
#
# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#
#
#
router = routers.DefaultRouter()
# router.register(r'users', UserSerializer)
router.register(r'places', views.PlaceViewSet)
router.register(r'activities', views.ActivityViewSet)
router.register(r'users', views.UserViewSet, base_name='users')
router.register(r'expenses', views.ExpenseViewSet)
router.register(r'memberships', views.MembershipViewSet)
router.register(r'travelgroups', views.TravelGroupViewSet, base_name='travelgroups')
router.register(r'friends', views.FriendshipViewSet)
router.register(r'messages', views.MessageViewset, base_name='messages')
router.register(r'notifications', views.NotificationViewset, base_name='notifications')

urlpatterns = [
    # path('user/register', views.register),
    # path('user/show', views.show),
    # path('user/update', views.update),
    #url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('user/login/', views.SessionLoginView.as_view()),
    url(r'^', include(router.urls)),
    #url(r'^user/get_auth_token/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),
    url(r'^user/get_auth_token/$', views.obtain_expiring_auth_token, name='get_auth_token'),
    # url(r'^notifications/$', views.NotificationViewset.as_view(queryset=models.Notification.objects.all(), serializer_class=NotificationSerializer), name='notifications')
]