from django.conf.urls import url, include

from ir_model import IRModel
from . import views

print("Hallo!")

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^search$', views.search)
]

m = IRModel.get_instance()