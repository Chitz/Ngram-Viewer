from django.conf.urls import url

from ngram_viewer_app import views

urlpatterns = [
    url(r'^$', views.get, name = "get"),
]