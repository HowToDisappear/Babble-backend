# Generated by Django 3.2.5 on 2021-11-18 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_contact_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='about',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='username',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]