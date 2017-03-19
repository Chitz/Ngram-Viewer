from django.conf.urls import url

from ngram_viewer_app import views

urlpatterns = [
    #url(r'^$', views.HomePageView.as_view()),
    url(r'^$', views.get, name = "get"),
    #url(r'^$', views.view_ngram),
]