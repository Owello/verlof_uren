# Generated by Django 2.2 on 2019-04-10 14:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0003_auto_20190410_1436'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leaveregistration',
            name='user',
        ),
    ]
