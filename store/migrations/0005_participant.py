# -*- coding: utf-8 -*-
# Generated by Django 1.11b1 on 2017-07-07 09:39
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_app_screenshot'),
    ]

    operations = [
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task', models.SmallIntegerField()),
                ('condition', models.SmallIntegerField()),
                ('time_start', models.TimeField(auto_now_add=True)),
                ('time_end', models.TimeField()),
                ('profiler_answers', jsonfield.fields.JSONField()),
                ('page_nav_route', jsonfield.fields.JSONField()),
                ('debrief_questions', jsonfield.fields.JSONField()),
                ('debrief_answers', jsonfield.fields.JSONField()),
            ],
        ),
    ]
