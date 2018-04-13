from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import ObjectDoesNotExist, FieldDoesNotExist
from django.core.validators import validate_email
from django.core.exceptions import  ValidationError
from wire_profile.models import Follow


def register(request):
    """
    Create a user using the information sent by a POST request. Perform backend validation on the email.
    Handle error messages for invalid email addresses and whether the username has already been taken

    :param request: The current request
    :return: Redirect the user to the appropriate page, with any necessary messages
    """
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')

    """
    Perform some backend validation
    """
    if not username:
        messages.error(request, 'Please enter a username', extra_tags='danger')
    elif len(username) > 150:
        messages.error(request, 'The maximum number of characters for a username is 150', extra_tags='danger')
    if not password:
        messages.error(request, 'Please enter a password', extra_tags='danger')
    if not email:
        messages.error(request, 'Please enter an email address', extra_tags='danger')
    elif len(email) > 254:
        messages.error(request, 'The maximum number of characters for an email address is 254', extra_tags='danger')

    """
    If any of the backend validation has failed, redirect back to the sign in page
    TODO: Add functionality to refill the form with any data the user has input
    """
    if len(messages.get_messages(request)) != 0:
        return HttpResponseRedirect(reverse('base:signup'))

    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, 'Please enter a valid email address', extra_tags='danger')
        return HttpResponseRedirect(reverse('base:signup'))

    try:
        user = User.objects.create_user(username, email, password)
    except IntegrityError:
        messages.error(request, 'That username already exists', extra_tags='danger')
        return HttpResponseRedirect(reverse('base:signup'))
    except ValueError:
        messages.error(request, 'Please ensure you have entered a username, email, and password', extra_tags='danger')
        return HttpResponseRedirect(reverse('base:signup'))

    login(request, user)
    messages.success(request, 'Welcome to Wire, ' + user.username)
    return HttpResponseRedirect(reverse('base:home'))


def verify_user(request):
    """
    Validate the username and password provided by the request

    :param request: The request that called this function
    :return: If the username and password is valid, log the user in and redirect to the home page. Else, redirect the
             user to the log in page and show an error message
    """
    username = request.POST.get('username')
    password = request.POST.get('password')

    """
    Perform some backend validation
    """
    if not username:
        messages.error(request, 'Please enter a username', extra_tags='danger')
    elif len(username) > 150:
        messages.error(request, 'The maximum number of characters for a username is 150', extra_tags='danger')
    if not password:
        messages.error(request, 'Please enter a password', extra_tags='danger')

    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        messages.success(request, 'Welcome back, ' + user.username)
        return HttpResponseRedirect(reverse('base:home'))
    else:
        messages.error(request, 'Your username or password is incorrect', extra_tags='danger')
        return HttpResponseRedirect(reverse('base:login'))


def log_out(request):
    """
    Log the user out of the current session

    :param request: The request that called this function
    :return: Log the user out and return to the home page
    """
    logout(request)
    messages.success(request, 'You have logged out successfully')
    return HttpResponseRedirect(reverse('base:home'))


def recommended_users(request, excluded_username):
    """
    Return five users that is not the logged in user, anyone followed by the logged in user, or the specified excluded
    user

    :param request: The request that called this function
    :param excluded_username: A user not to include in the list
    :return: JSON list of users
    """
    try:
        if request.user.is_authenticated:
            follow_query = Follow.objects.filter(follower_id=request.user)
            users = User.objects.filter().exclude(id=request.user.id).exclude(username=excluded_username)\
                .exclude(followed_user__in=follow_query).values('username')[:5]
            return JsonResponse(list(users), safe=False)

        users = User.objects.filter().exclude(username=excluded_username).values('username')[:5]
        return JsonResponse(list(users), safe=False)

    except (ObjectDoesNotExist, FieldDoesNotExist):
        messages.error(request, 'Error retrieving recommended users. Please Contact IT', extra_tags='danger')
        return HttpResponseRedirect(reverse('base:home'))