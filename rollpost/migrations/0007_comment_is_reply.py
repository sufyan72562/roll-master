# Generated by Django 3.2.16 on 2022-12-24 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rollpost', '0006_auto_20221224_1940'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_reply',
            field=models.BooleanField(default=0),
        ),
    ]