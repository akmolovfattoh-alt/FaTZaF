from django.conf import settings
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    bio = models.CharField(max_length=180, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    last_seen = models.DateTimeField(null=True, blank=True)
    def __str__(self): return self.user.username

class Contact(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_contacts')
    person = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='added_by')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['owner','person'], name='unique_saved_contact')]

class Chat(models.Model):
    DIRECT = 'direct'
    GROUP = 'group'
    CHANNEL = 'channel'
    CHAT_TYPES = [(DIRECT, 'Личный чат'), (GROUP, 'Группа'), (CHANNEL, 'Канал')]
    title = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=300, blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chats')
    admins = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='managed_chats', blank=True)
    chat_type = models.CharField(max_length=10, choices=CHAT_TYPES, default=DIRECT)
    is_group = models.BooleanField(default=False)  # compatibility with existing database/templates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return self.title or 'Chat #' + str(self.pk)

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    body = models.TextField(max_length=5000)
    forwarded_from = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='forwards')
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    class Meta: ordering = ['created_at']
