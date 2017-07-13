# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from .models import Category,App,HeuristicScore,Participant

# Register your models here.
admin.site.register(Category)
admin.site.register(App)
admin.site.register(HeuristicScore)
admin.site.register(Participant)
