# Generated by Django 3.2.16 on 2023-04-26 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rollpost', '0014_auto_20230426_1908'),
    ]

    operations = [
        migrations.AlterField(
            model_name='posts',
            name='image',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='threadpost',
            name='image',
            field=models.TextField(blank=True),
        ),
    ]
