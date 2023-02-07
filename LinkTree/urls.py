from django.urls import path
from . import views
from .views import listfunc

app_name = 'LinkTree'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('list/', listfunc, name='list'),
]
