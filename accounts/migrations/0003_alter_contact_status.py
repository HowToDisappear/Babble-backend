# Generated by Django 3.2.5 on 2021-10-07 08:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20211002_0907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='status',
            field=models.IntegerField(choices=[(1, 'active'), (2, 'blocked'), (3, 'invited'), (4, 'friend')]),
        ),
    ]
