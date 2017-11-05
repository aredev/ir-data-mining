from django.conf.urls import url

from ir_model import IRModel
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search$', views.search),

    url(r'^author/(?P<author_id>[0-9]+)/$', views.getAuthorById)
]

m = IRModel.get_instance()
