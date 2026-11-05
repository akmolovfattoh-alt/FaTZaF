import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('OurSite', '0001_initial'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.AddField(model_name='profile', name='last_seen', field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name='chat', name='description', field=models.CharField(blank=True, max_length=300)),
        migrations.AddField(model_name='chat', name='chat_type', field=models.CharField(choices=[('direct', 'Личный чат'), ('group', 'Группа'), ('channel', 'Канал')], default='direct', max_length=10)),
        migrations.AddField(model_name='chat', name='admins', field=models.ManyToManyField(blank=True, related_name='managed_chats', to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name='message', name='forwarded_from', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='forwards', to='OurSite.message')),
        migrations.RunPython(
            code=lambda apps, schema_editor: apps.get_model('OurSite', 'Chat').objects.filter(is_group=True).update(chat_type='group'),
            reverse_code=migrations.RunPython.noop,
        ),
    ]
