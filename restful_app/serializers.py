from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *


class FriendCreateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        me = validated_data['me']
        friendship = Friendship.objects.create(user1=me,
                                               user2=validated_data['user2'])
        friendship.save()
        return friendship

    class Meta:
        model = Friendship
        fields = ('user2', )


class UserFriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', )


class FriendSerializer(serializers.ModelSerializer):
    user = UserFriendSerializer(many=False, read_only=True, source='user1')
    class Meta:
        model = Friendship
        fields = ('created_time', 'user', )


class ProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ('birth', 'gender', )


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', )


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def create(self, validated_data):
        return User.objects.create_user(username=validated_data['username'], password=validated_data['password'], email=validated_data['email'])


class NotificationSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(slug_field="username", many=False, read_only=True)
    class Meta:
        model = Notification
        fields = ('id', 'source', 'content', 'subject', 'created_time', 'is_read')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(many=False, read_only=True)
    friend = FriendSerializer(many=True, read_only=True, )
    # received_notification = NotificationSerializer(many=True, read_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'profile', 'friend', )


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'id')


class ExpenseCreateUpdateSerializer(serializers.ModelSerializer):

    def validate_payees(self, users):
        print(self.initial_data)
        paid_member_id = self.initial_data['paid_member']
        paid_member = Membership.objects.get(pk=paid_member_id)
        travel_group = paid_member.travel_group
        group_users = travel_group.users.all()
        for user in users:
            if user not in group_users:
                raise serializers.ValidationError("User '" + str(user) + "' is not in travel group '" + str(travel_group) + "'")
        return users

    def create(self, validated_data):
        expense = Expense.objects.create(
            paid_member=validated_data['paid_member'],
            expense=validated_data['expense'],
            comment=validated_data['comment'],
        )
        expense.payees.set(validated_data['payees'])
        expense.save()
        return expense

    def update(self, instance, validated_data):
        instance.expense=validated_data['expense']
        instance.comment=validated_data['comment']
        instance.payees.set(validated_data['payees'])
        instance.save()
        return instance

    class Meta:
        model = Expense
        fields = ('expense', 'paid_member', 'payees', 'comment', )


class ExpenseSerializer(serializers.ModelSerializer):
    payees = UserNameSerializer(many=True, read_only=True)

    class Meta:
        model = Expense
        fields = ('id', 'payees', 'expense', 'comment', 'paid_member')
        extra_kwargs = {'paid_member': {'read_only': True}}

class MembershipSerializer(serializers.ModelSerializer):
    user = UserNameSerializer(many=False, read_only=True)
    expense_set = ExpenseSerializer(many=True, read_only=True)
    class Meta:
        model = Membership
        #fields = '__all__'
        fields = ('id', 'user', 'travel_group', 'is_manager', 'is_creator', 'expense_set')
        extra_kwargs = {'is_creator': {'read_only': True}, 'user': {'read_only': True}, 'travel_group': {'read_only': True}}


class MembershipCreateSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        print(validated_data)
        return Membership.objects.create(user=validated_data['user'], travel_group=validated_data['travel_group'])

    class Meta:
        model = Membership
        #fields = '__all__'
        fields = ('user', 'travel_group', 'is_manager', 'is_creator')
        extra_kwargs = {'is_creator': {'read_only': True}}


class MessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ('username', 'message', 'created_time', )





class TravelGroupDetailSerializer(serializers.ModelSerializer):
    membership_set = MembershipSerializer(many=True, read_only=True)
    message_set = MessageSerializer(many=True, read_only=True)
    class Meta:
        model = TravelGroup
        fields = ('id', 'title', 'is_public', 'country', 'days', 'modified_time', 'membership_set', 'message_set', )


class TravelGroupCreateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        travelgroup = TravelGroup.objects.create(
            title=validated_data['title'],
            is_public=validated_data['is_public'],
            country=validated_data['country'],
            days=validated_data['days']
        )
        creator = validated_data['creator']
        Membership.objects.create(user=creator, travel_group=travelgroup, is_creator=True)
        return travelgroup

    class Meta:
        model = TravelGroup
        fields = ('title', 'is_public', 'country', 'days')


class TravelGroupUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelGroup
        fields = ('title', 'is_public', 'country', 'days')


class TravelGroupListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelGroup
        fields = ('id', 'title', 'is_public', 'country', 'days')


class PlaceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        # fields = ('id', 'name', 'description', 'location', 'country', 'city', 'user', 'is_public', 'editable')
        fields = '__all__'

class PlaceSerializer(serializers.ModelSerializer):
    # user = serializers.ReadOnlyField(source='user.username')
    # user = serializers.SlugRelatedField(queryset=WebUser.objects.all(), slug_field='username')
    # user = UserSerializer(many=False, read_only=True)
    class Meta:
        model = Place
        fields = ('id', 'name', 'description', 'location', 'country', 'city', 'is_public')


class ActivityPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ('id', 'name')


class ActivitySerializer(serializers.ModelSerializer):
    # travel = serializers.PrimaryKeyRelatedField(queryset=TravelPlan.objects.all())
    # travel = TravelSerializer(many=False, read_only=True)
    travel = serializers.SlugRelatedField(many=False, read_only=True, slug_field='title')
    # place = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    place = ActivityPlaceSerializer(many=False, read_only=True)
    # expenses = serializers.SlugRelatedField(queryset=Expense.objects.all(), slug_field='expense')

    class Meta:
        model = Activity
        fields = ('id', 'start_time', 'duration', 'activity', 'note', 'travel', 'place', )


class ActivityCreateSerializer(serializers.ModelSerializer):
    # def create(self, validated_data):
    #     print(validated_data)

    class Meta:
        model = Activity
        fields = ('id', 'start_time', 'activity', 'note', 'travel', 'place')