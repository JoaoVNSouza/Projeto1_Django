# Generated by Django 5.1 on 2024-08-27 17:41

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('investidores', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='propostainvestimento',
            name='data',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
