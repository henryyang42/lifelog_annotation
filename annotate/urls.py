from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.annotate, name='annotate'),
    url(r'^show/$', views.list_sentence, name='list_sentence'),
    url(r'^progress/$', views.progress, name='progress'),
    url(r'^download/$', views.download_annotation, name='download'),
    url(r'^make_framenet/$', views.make_framenet, name='make_framenet'),
]
