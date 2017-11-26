from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<paper_id>[0-9]+)/$', views.get_paper_by_id)
]