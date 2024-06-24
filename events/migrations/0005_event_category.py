# Generated by Django 4.2.13 on 2024-06-22 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0004_message_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='category',
            field=models.CharField(choices=[('MUSIC', 'Music'), ('SPORTS', 'Sports'), ('ARTS', 'Arts & Culture'), ('FOOD', 'Food & Drink'), ('OTHER', 'Other')], default='OTHER', max_length=20),
        ),
    ]
