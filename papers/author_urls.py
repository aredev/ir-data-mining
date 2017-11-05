from django.conf.urls import url

from ir_model import IRModel
from . import views

urlpatterns = [
    url(r'^(?P<author_id>[0-9]+)/$', views.getAuthorById)
]