# Generated by Django 3.2.16 on 2023-07-10 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rollchat', '0002_conversation_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='image',
            field=models.TextField(blank=True, null=True),
        ),
    ]
