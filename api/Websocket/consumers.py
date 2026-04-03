import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User


class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        await self.send(text_data=text_data)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.username = self.scope['url_route']['kwargs']['username']
        self.group_name = f'chat_{self.room_name}'

        if not await self._user_exists(self.username):
            await self.close()
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat_message',
            'event': 'join',
            'username': self.username,
        })

    async def disconnect(self, code):
        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat_message',
            'event': 'leave',
            'username': self.username,
        })
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        await self.channel_layer.group_send(self.group_name, {
            'type': 'chat_message',
            'event': 'message',
            'username': self.username,
            'message': data.get('message', ''),
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def _user_exists(self, username):
        return User.objects.filter(username=username).exists()


class modelChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated:
            await self.close()
            return
        await self.accept()

    async def disconnect(self, code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data.get('message', '')

        if message.startswith('info:'):
            name = message[5:].strip()
            results = await self._query_test(name)
            await self.send(text_data=json.dumps({'results': results}))
        else:
            await self.send(text_data=json.dumps({'error': 'Unknown command'}))

    @database_sync_to_async
    def _query_test(self, name):
        from api.TestAPI.model import Test
        qs = Test.objects.filter(name__icontains=name).values('id', 'name', 'description')
        return [{'id': str(r['id']), 'name': r['name'], 'description': r['description']} for r in qs]
