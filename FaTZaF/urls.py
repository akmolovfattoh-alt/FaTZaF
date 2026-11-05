from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from OurSite import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('contacts/add/<int:user_id>/', views.add_contact, name='add_contact'),
    path('chats/create/', views.create_chat, name='create_chat'),
    path('chat/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('message/<int:message_id>/forward/', views.forward_message, name='forward_message'),
    path('message/<int:message_id>/edit/', views.edit_message, name='edit_message'),
    path('message/<int:message_id>/delete/', views.delete_message, name='delete_message'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
