from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Connection, Message
from django.contrib.auth.models import User
import json
from django.core.files.base import ContentFile
import base64

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        delete_message_id = data.get('delete_message_id', None)
        if delete_message_id:
            await self.handle_delete_message(delete_message_id)
            return

        message = data.get('message', None)
        sender_username = data.get('sender',None)
        reply_to_id = data.get('reply_to', None)
        file_data = data.get('data')  # Base64 encoded file data
        if file_data:

            format, file_str = file_data.split(';base64,')
            ext = format.split('/')[-1]  # Get the file extension (e.g., 'png', 'pdf', etc.)
            filename = f"{data['filename']}.{ext}"

            # Decode the file and save it to the server
            file_content = ContentFile(base64.b64decode(file_str), name=filename)
        else:
            file_content = None

        # Get sender and connection objects asynchronously
        sender = await sync_to_async(self.get_user)(sender_username)
        connection = await sync_to_async(self.get_connection)()
        
        if reply_to_id:
            reply_to_message = await sync_to_async(Message.objects.get)(id=reply_to_id)

            # Create a new message that references the reply_to_message
            message = await sync_to_async(Message.objects.create)(
                connection=connection,
                sender=sender,
                message=message,
                attachment=file_content,
                reply_to=reply_to_message  # Associate this message as a reply
            )
        else:
            # Create a new message without a reply
           message = await sync_to_async(Message.objects.create)(
            connection=connection,
            sender=sender, 
            message=message,
            attachment = file_content
           )
        message.is_read = False
        await sync_to_async(message.save)()

        # Broadcast the message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.message,
                'sender': sender.username,
                'attachment': message.attachment.url if message.attachment else None,
                'message_id': message.id,
                'reply_to': message.reply_to.id if message.reply_to else None,
                'timestamp': message.timestamp.strftime('%b. %d, %Y, %I:%M %p'),
            }
        )
    async def chat_message(self, event):
        messege = event['message']
        sender = event['sender']
        attachment = event['attachment']
        message_id = event['message_id']
        reply_to = event['reply_to']
        timestamp = event['timestamp'] 


        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'message': messege,
            'sender' : sender,
            'attachment' : attachment,
            'message_id': message_id, 
            'reply_to': reply_to,  
            'timestamp': timestamp, 

        }))
    
    async def message_deleted(self, event):
            # Notify all users that a message has been deleted
            await self.send(text_data=json.dumps({
                'action': 'delete',
                'message_id': event['message_id'],
            }))
    async def handle_delete_message(self, message_id):
        try:
            message_to_delete = await sync_to_async(Message.objects.get)(id=message_id)
            message_to_delete.deleted = True
            await sync_to_async(message_to_delete.save)()
            # Notify all users in the room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_deleted',
                    'message_id': message_id,
                }
            )
        except Message.DoesNotExist:
            # Optionally log or handle this case
            pass

    @staticmethod
    def get_user(username):
        return User.objects.get(username=username)

    def get_connection(self):
        return Connection.objects.get(room_name=self.room_name)
    