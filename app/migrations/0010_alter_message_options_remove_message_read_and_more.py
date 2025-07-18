# Generated by Django 5.0.1 on 2025-07-02 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_remove_profile_followers'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={},
        ),
        migrations.RemoveField(
            model_name='message',
            name='read',
        ),
        migrations.AddField(
            model_name='message',
            name='deleted_for_receiver',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='deleted_for_sender',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='deleted_globally',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='profile',
            name='profile_pic',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
