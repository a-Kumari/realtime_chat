from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from .models import Message, Connection, Profile
from .forms import ProfileForm
from django.db.models import Q


def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('connection')  
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('base')



@login_required
def connection(request):
    # Get all users excluding admin and the current user
    users = User.objects.exclude(Q(username='admin') | Q(username=request.user.username))
    
    # Iterate through users to create context
    user_list = []
    for user in users:
        sender = request.user
        receiver = user
        # Check if a connection already exists
        existing_connection = Connection.objects.filter(
            Q(sender=sender, receiver=receiver) | Q(sender=receiver, receiver=sender)
        ).first()

        # If connection exists, use its room_name; otherwise, create a new one
        if existing_connection:
            room_name = existing_connection.room_name
        else:
            # Create a unique room name and save it in the database
            room_name = f"chat_{sender.username}_{receiver.username}"
            Connection.objects.create(sender=sender, receiver=receiver, room_name=room_name)
        unread_count = Message.objects.filter(Q(connection__room_name=room_name)& Q(is_read=False)& Q(sender=receiver)).count()
        user_list.append({
            'username': receiver.username,
            'profile_picture': receiver.profile.profile_picture,
            'about': receiver.profile.about,
            'room_name': room_name,
            'unread_count': unread_count, 
        })

    context = {
        'users': user_list
    }
    return render(request, 'connection.html', context)

@login_required
def chat_room(request, room_name):
    connection = Connection.objects.filter(room_name=room_name).first()
    if not connection:
        return redirect('connection')

    
    if connection.sender == request.user:
        unread_messages = Message.objects.filter(connection=connection, sender=connection.receiver, is_read=False)
    else:
        unread_messages = Message.objects.filter(connection=connection, sender=connection.sender, is_read=False)
        
    unread_messages.update(is_read=True)

    messages = Message.objects.filter(connection=connection, deleted=False).order_by('timestamp')
    for message in messages:
        if message.reply_to:
            replied_message = message.reply_to.message  
            message.replied_message = replied_message 
            replied_sender = message.reply_to.sender.username
            message.replied_username = replied_sender 

    return render(request, 'chat_room.html', {
        'room_name': room_name,
        'connection': connection,
        'messages': messages,
        "current_user": request.user,  # Pass the current logged-in user
    })

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        profile = form.save(commit=False)
        profile.user = request.user  
        profile.save()
    else:
        form = ProfileForm()
    return render(request, 'profile.html', {'form': form})

def base(request):
    return render(request,'base.html' )