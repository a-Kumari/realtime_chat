
from django.contrib import admin
from django.urls import path
from chat import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('connection', views.connection, name='connection'),
    path('chat/<str:room_name>/', views.chat_room, name='chat_room'),
    path('profile/', views.profile, name='profile'),
    path('', views.base, name='base'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
