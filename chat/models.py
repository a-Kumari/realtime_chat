
from django.contrib.auth.models import User
from django.db import models
import emoji

class Connection(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="connections_as_sender")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="connections_as_receiver")
    room_name = models.CharField(max_length=50)

    def __str__(self):
        return f'Connection: {self.sender} <-> {self.receiver} in {self.room_name}'

class Message(models.Model):
    connection = models.ForeignKey(Connection, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")  
    message = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')  # For replies
    deleted = models.BooleanField(default=False)  # To mark deleted messages




    def __str__(self):
        return f'Message from {self.sender.username}: {self.message[:30]}'

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pics/')
    about = models.TextField(max_length=100, blank=True, default="Hi there! I'm using this ChitChat.")

    def __str__(self):
        return f"{self.user.username}'s Profile"