from django.shortcuts import render
from django.views import generic

from .forms import Form

# Create your views here.

class IndexView(generic.FormView):
    template_name = "index.html"
    form_class = Form
