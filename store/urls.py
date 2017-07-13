from django.conf.urls import include, url
from django.contrib import admin

from . import views

urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^consent$', views.consent, name="consent"),
    url(r'^profiler$', views.profiler, name="profiler"),
    url(r'^nextp$', views.next_profile, name="next_profile"),
    url(r'^doneProfiler$', views.done_profiler, name="done_profiler"),
    url(r'^clear$', views.clear, name="clear"),
    url(r'^storeHome$', views.store_home, name="store_home"),
    url(r'^category$', views.category, name="category"),
    url(r'^app$', views.app_listing, name="app"),
    url(r'^tasks$', views.tasks, name="tasks"),
    url(r'^postTask$', views.post_task, name="post_task"),
    url(r'^bulk$', views.bulk_import, name="bulk_import"),
    url(r'^postBrief$', views.post_brief, name="post_brief"),
    url(r'^postInstall$', views.post_install, name="post_install"),
    url(r'^qsExp$', views.qs_exp, name="qs_exp"),
    url(r'^error$', views.error, name="error"),
    url(r'^saveResponses$', views.save_responses, name="save_responses"),
    url(r'^submitBrief$', views.submit_brief, name="submit_brief")

]
