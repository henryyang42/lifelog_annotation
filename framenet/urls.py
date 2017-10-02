from django.conf.urls import url
from . import api
from . import views

urlpatterns = [
    url(r'^lu/$', api.lu, name='lu'),
    url(r'^framenet/$', api.framenet, name='framenet'),
    url(r'^tokenize/$', api.tokenize_s, name='tokenize'),
    url(r'^annotate/$', views.annotate, name='annotate'),
]
