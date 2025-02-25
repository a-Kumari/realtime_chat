from django.contrib import admin
from .models import Message, Connection, Profile
admin.site.register(Message)
admin.site.register(Connection)
admin.site.register(Profile)