# -*- coding: utf-8 -*-
# Generated by Django 1.11b1 on 2017-05-10 10:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='description_dom',
            field=models.CharField(max_length=10000),
        ),
    ]
