# Generated by Django 3.1.6 on 2021-02-11 17:42

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('Search', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2021, 2, 11, 17, 42, 17, 466589, tzinfo=utc)),
        ),
    ]
