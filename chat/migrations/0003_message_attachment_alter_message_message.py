# Generated by Django 5.1.4 on 2024-12-19 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='chat_attachments/'),
        ),
        migrations.AlterField(
            model_name='message',
            name='message',
            field=models.TextField(blank=True, null=True),
        ),
    ]
