import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage

class AdminChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_staff:
            await self.channel_layer.group_add("admin_chat", self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("admin_chat", self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        message_type = text_data_json.get('type', 'ADMIN')

        # Lưu tin nhắn vào database
        await self.save_message(message, message_type)

        # Gửi tin nhắn đến tất cả admin đang online
        await self.channel_layer.group_send(
            "admin_chat",
            {
                "type": "chat_message",
                "message": message,
                "message_type": message_type
            }
        )

    async def chat_message(self, event):
        message = event["message"]
        message_type = event["message_type"]

        await self.send(text_data=json.dumps({
            "message": message,
            "type": message_type
        }))

    @database_sync_to_async
    def save_message(self, content, message_type):
        ChatMessage.objects.create(
            content=content,
            sender_type=message_type,
            sender_name=self.scope["user"].username
        )