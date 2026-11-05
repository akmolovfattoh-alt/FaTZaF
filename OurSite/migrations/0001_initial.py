# Initial migration for the basic messenger.
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name='Chat', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('title', models.CharField(blank=True, max_length=100)), ('is_group', models.BooleanField(default=False)), ('created_at', models.DateTimeField(auto_now_add=True)), ('updated_at', models.DateTimeField(auto_now=True)), ('participants', models.ManyToManyField(related_name='chats', to=settings.AUTH_USER_MODEL))]),
        migrations.CreateModel(name='Profile', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('bio', models.CharField(blank=True, max_length=180)), ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/')), ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL))]),
        migrations.CreateModel(name='Contact', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('created_at', models.DateTimeField(auto_now_add=True)), ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='saved_contacts', to=settings.AUTH_USER_MODEL)), ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='added_by', to=settings.AUTH_USER_MODEL))], options={'constraints':[models.UniqueConstraint(fields=('owner','person'), name='unique_saved_contact')]}),
        migrations.CreateModel(name='Message', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('body', models.TextField(max_length=5000)), ('created_at', models.DateTimeField(auto_now_add=True)), ('edited_at', models.DateTimeField(blank=True, null=True)), ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='OurSite.chat')), ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL))], options={'ordering':['created_at']}),
    ]
