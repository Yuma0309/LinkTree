from django.urls import path

from . import views


app_name = 'LinkTree'
urlpatterns = [
    path('', views.IndexView.as_view(), name="index"),
]
