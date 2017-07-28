# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import OrderedDict

from django.db import models

from jsonfield import JSONField

class Participant(models.Model):
    task = models.SmallIntegerField()
    condition = models.SmallIntegerField() # 0: control, 1: generic, 2: personalised
    time_start = models.DateTimeField( =True)
    time_end = models.DateTimeField(null=True)
    profiler_answers = JSONField()
    page_nav_route = JSONField()
    debrief_questions = JSONField()
    debrief_answers = JSONField()


class Category(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)

class App(models.Model):
    package = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    icon_url = models.URLField(max_length=200)
    description_dom = models.CharField(max_length=10000)
    category = models.ForeignKey(Category)
    short_description = models.CharField(max_length=200)
    screenshot = models.URLField(max_length=200)



class HeuristicScore(models.Model):
    app = models.ForeignKey(App)
    heuristic_no = models.SmallIntegerField()
    score = models.SmallIntegerField()

    @property
    def max_score(self):
        """ Returns the maximum possible score for this heuristic """
        h_ranges = [2,2,2,2,2,4,2,2,2,2,2,3,3,3,2,3,2,2,2,2,1,2,1,1,1,2]
        return h_ranges[self.heuristic_no]

    @property
    def category(self):
        """
            Returns the category this heuristic belongs to
        """
        h_cats = OrderedDict([(7,"notice"),(15,"consent"),(19,"access"),(26,"social")])

        for hc in h_cats.keys():
            if self.heuristic_no < hc:
                return h_cats[hc]
