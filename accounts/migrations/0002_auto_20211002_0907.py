# Generated by Django 3.2.5 on 2021-10-02 09:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='inviter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='contact_inviter', to='accounts.account'),
        ),
        migrations.AlterField(
            model_name='account',
            name='contacts',
            field=models.ManyToManyField(related_name='_accounts_account_contacts_+', through='accounts.Contact', to='accounts.Account'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='status',
            field=models.IntegerField(choices=[(1, 'active'), (2, 'blocked'), (3, 'invited')]),
        ),
    ]
