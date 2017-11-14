from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


def register(request):
    request_data = request.POST
    user = User.objects.create_user(request_data.get('username'), request_data.get('email'), request_data.get('password'))
    return HttpResponseRedirect(reverse('base:home'))


def verify_user(request):
    request_data = request.POST
    user = authenticate(username=request_data.get('username'), password=request_data.get('password'))
    if user is not None:
        return HttpResponseRedirect(reverse('base:home'))
    else:
        return HttpResponseRedirect(reverse('base:signup'))
