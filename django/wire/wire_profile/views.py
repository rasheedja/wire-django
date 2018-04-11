from django.shortcuts import render
from django.template.loader import get_template
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.db import DatabaseError
from django.db.models import ObjectDoesNotExist, FieldDoesNotExist
from django.core import serializers
from .forms import NewWireForm
from .models import Message

# Create your views here.


class ProfileView(TemplateView):
    template_name = "wire_profile/profile.html"

    def get(self, request, *args, **kwargs):
        """
        Get the current profile if the user is logged in. Show the search
        page if the user is not logged in.

        :param request: The current request
        :param args: sent to parent method
        :param kwargs: sent to parent method
        :return: Either redirect to the search page or render the profile page
        """
        username = request.GET.get('username')
        context = self.get_context_data(**kwargs)
        context['is_current_user'] = False

        form = NewWireForm()
        context['form'] = form

        if username is None:
            if request.user.is_authenticated:
                context['is_current_user'] = True
                context['user'] = request.user
                context['user_messages'] = Message.objects.filter(user=request.user)
                return self.render_to_response(context)
            else:
                return HttpResponseRedirect(reverse('base:home'))
        else:
            try:
                user = User.objects.get(username=username)
                if user == request.user:
                    context['is_current_user'] = True

                context['user'] = user
                context['user_messages'] = Message.objects.filter(user=user)
                return self.render_to_response(context)

            except (ObjectDoesNotExist, FieldDoesNotExist):
                messages.error(request, 'The requested user was not found', extra_tags='danger')
                return HttpResponseRedirect(reverse('base:home'))


def create_message(request):
    """
    Create a message for the logged in user

    :param request: The request sent by the user
    :return: Display the profile page with a relevant message
    """
    if request.method == 'POST':
        form = NewWireForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                message = form.cleaned_data['message']
                try:
                    Message.objects.create(message_text=message, created=timezone.now(), user=request.user)
                    messages.success(request, 'Message created successfully', extra_tags='success')
                    return HttpResponseRedirect(reverse('wire_profile:profile'))
                except DatabaseError:
                    messages.error(request, 'Error creating message, please contact support', extra_tags='danger')
                    return HttpResponseRedirect(reverse('wire_profile:profile'))
            else:
                messages.error(request, 'Sorry, only registered users can create messages', extra_tags='danger')
                return HttpResponseRedirect(reverse('base:home'))
        else:
            messages.error(request, 'Please enter a message', extra_tags='danger')
            return HttpResponseRedirect(reverse('base:home'))
    else:
        messages.error(request, 'Sorry, you cannot access that URL', extra_tags='danger')
        return HttpResponseRedirect(reverse('base:home'))


def get_messages(request, username):
    """
    Retrieve messages for the given username in JSON format

    :param request: The request sent by the user
    :param username: The username to retrieve messages for
    :return:
    """
    try:
        user = User.objects.get(username=username)
        userMessages = Message.objects.filter(user=user).values('message_text', 'created', 'user')
        return JsonResponse(list(userMessages), safe=False)

    except (ObjectDoesNotExist, FieldDoesNotExist):
        messages.error(request, 'The requested user was not found', extra_tags='danger')
        return HttpResponseRedirect(reverse('base:home'))