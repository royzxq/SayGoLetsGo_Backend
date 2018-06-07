from channels.generic.websocket import WebsocketConsumer
import json
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.apps import apps
Message = apps.get_model('restful_app', 'Message')
TravelGroup = apps.get_model('restful_app', 'TravelGroup')
Notification = apps.get_model('restful_app', 'Notification')

class ChatConsumer(WebsocketConsumer):

    def connect(self):
        self.group_id = self.scope['url_route']['kwargs']['group_id']
        # self.user_name = self.scope['user']
        self.room_group_name = 'chat_%s' % self.group_id
        self.group = TravelGroup.objects.get(pk=self.group_id)
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        m = Message(username=username, message=message, travel_group=self.group)
        m.save()
        # Send message to room group
        async_to_sync (self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'created_time': m.created_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'username': event['username'],
            'created_time': event['created_time'],
        }))


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = 'user_%s' % self.user_id
        self.target_user = User.objects.get(pk=self.user_id)
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, code):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        content = text_data_json['content']
        source = text_data_json['source']
        subject = text_data_json['subject']
        source = User.objects.get(username=source)
        n = Notification(source=source, content=content, target=self.target_user, subject=subject)
        n.save()
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'user_notification',
                'content': content,
                'subject': subject,
                'source': source.username,
                'created_time': n.created_time.strftime('%Y-%m-%d %H:%M:%S'),
            }
        )

    def user_notification(self, event):
        content = event['content']
        subject = event['subject']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'content': content,
            'subject': subject,
            'source': event['source'],
            'created_time': event['created_time'],
        }))
