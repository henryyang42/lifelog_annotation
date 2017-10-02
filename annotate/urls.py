from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.annotate, name='annotate'),
    url(r'^show/$', views.list_sentence, name='list_sentence'),
]
