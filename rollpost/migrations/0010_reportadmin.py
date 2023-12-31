# Generated by Django 3.2.16 on 2023-01-12 11:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rollpost', '0009_auto_20221226_0415'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reportcomment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='rollpost.comment')),
                ('reportpost', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='rollpost.posts')),
                ('reportuser', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reportuser', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
