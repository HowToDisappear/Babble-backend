# Generated by Django 3.2.5 on 2021-10-07 08:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_alter_membership_status'),
        ('chats', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='groupmessage',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='groups.topic'),
        ),
    ]
