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
from .forms import NewWireForm, SearchForm
from .models import Message, Follow

# Create your views here.


class ProfileView(TemplateView):
    template_name = "wire_profile/profile.html"

    def get(self, request, *args, **kwargs):
        """
        Get the profile page of the given user. Show the search page if the user was not found

        :param request: The current request
        :param args: sent to parent method
        :param kwargs: sent to parent method
        :return: Either redirect to the search page or render the profile page
        """
        username = self.kwargs['username'].rstrip('/')
        context = self.get_context_data(**kwargs)
        context['is_current_user'] = False

        try:
            user = User.objects.get(username=username)
            context['user'] = user
            context['user_messages'] = Message.objects.filter(user=user)
            return self.render_to_response(context)

        except (ObjectDoesNotExist, FieldDoesNotExist):
            messages.error(request, 'The requested user was not found', extra_tags='danger')
            url = reverse('wire_profile:search_user', kwargs={'query': username})
            return HttpResponseRedirect(url)


class CurrentProfileView(TemplateView):
    template_name = "wire_profile/current_profile.html"

    def get(self, request, *args, **kwargs):
        """
        Get the current profile if the user is logged in.

        :param request: The current request
        :param args: sent to parent method
        :param kwargs: sent to parent method
        :return: Either redirect to the search page or render the profile page
        """
        if request.user.is_authenticated:
            context = self.get_context_data(**kwargs)
            form = NewWireForm()
            context['is_current_user'] = False
            context['form'] = form
            context['is_current_user'] = True
            context['user'] = request.user
            context['user_messages'] = Message.objects.filter(user=request.user)
            return self.render_to_response(context)
        else:
            messages.error(request, 'You must log in to view your profile page', extra_tags='danger')
            return HttpResponseRedirect(reverse('base:home'))


class SearchView(TemplateView):
    template_name = 'wire_profile/search.html'

    def get(self, request, *args, **kwargs):
        """
        Render the search page

        :param request: The current request
        :param args: sent to parent method
        :param kwargs: sent to parent method
        :return: Render the search page
        """
        context = self.get_context_data(**kwargs)
        context['form'] = SearchForm()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = SearchForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['is_wire_search'] == 'true':
                url = reverse('wire_profile:search_message', kwargs={'query': form.cleaned_data['search_query']})
                return HttpResponseRedirect(url)
            else:
                url = reverse('wire_profile:search_user', kwargs={'query': form.cleaned_data['search_query']})
                return HttpResponseRedirect(url)
        else:
            messages.error(request, 'Please complete the search form', extra_tags='danger')
            return HttpResponseRedirect(reverse('wire_profile:search'))



class SearchMessageView(TemplateView):
    template_name = 'wire_profile/search_message.html'

    def get(self, request, *args, **kwargs):
        """
        Render the matching messages for a search message query

        :param request: The current request
        :param args: sent to parent method
        :param kwargs: sent to parent method
        :return: Render the search message results page
        """
        query = self.kwargs['query']
        search_results = Message.objects.filter(message_text__icontains=query).all()
        context = self.get_context_data(**kwargs)
        context['search_results'] = search_results
        return self.render_to_response(context)


class SearchUserView(TemplateView):
    template_name = 'wire_profile/search_user.html'

    def get(self, request, *args, **kwargs):
        """
        Render the matching messages for a search message query

        :param request: The current request
        :param args: sent to parent method
        :param kwargs: sent to parent method
        :return: Render the search message results page
        """
        query = self.kwargs['query']
        search_results = User.objects.filter(username__icontains=query).all()
        context = self.get_context_data(**kwargs)
        context['search_results'] = search_results
        return self.render_to_response(context)


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
                    return HttpResponseRedirect(reverse('wire_profile:current_profile'))
                except DatabaseError:
                    messages.error(request, 'Error creating message, please contact support', extra_tags='danger')
                    return HttpResponseRedirect(reverse('wire_profile:current_profile'))
            else:
                messages.error(request, 'Sorry, only registered users can create messages', extra_tags='danger')
                return HttpResponseRedirect(reverse('base:home'))
        else:
            messages.error(request, 'Please enter a message', extra_tags='danger')
            return HttpResponseRedirect(reverse('wire_profile:current_profile'))
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
        user_messages = Message.objects.filter(user=user).order_by('-created').values('message_text', 'created', 'user')
        return JsonResponse(list(user_messages), safe=False)

    except (ObjectDoesNotExist, FieldDoesNotExist):
        messages.error(request, 'The requested user was not found', extra_tags='danger')
        return HttpResponseRedirect(reverse('base:home'))


def get_messages_by_ids(request, user_ids):
    """
    Retrieve messages for the given user ids in JSON format

    :param request: The request sent by the user
    :param user_ids: The user ids to retrieve messages for
    :return:
    """
    try:
        user_ids_list = filter(bool, user_ids.split('/'))
        user_ids_list = list(map(int, user_ids_list))
        users = User.objects.filter(pk__in=user_ids_list)
        user_messages = Message.objects.filter(user__in=users).order_by('-created').values('message_text', 'created', 'user')
        return JsonResponse(list(user_messages), safe=False)

    except (ObjectDoesNotExist, FieldDoesNotExist):
        messages.error(request, 'The requested users were not found', extra_tags='danger')
        return HttpResponseRedirect(reverse('base:home'))


def follow_user(request, username):
    """
    Follow the given username

    :param request: The request that called this function
    :param username: The user to follow
    :return: success or failure message in JSON format
    """
    username = username.rstrip('/')
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'You must be logged in to follow a user'})
    if request.user.username == username:
        return JsonResponse({'success': False, 'message': 'You cannot follow yourself!'})
    try:
        user = User.objects.get(username=username)
        maybe_following = Follow.objects.filter(follower_id=request.user).filter(following_id=user)
        if maybe_following.count() > 0:
            maybe_following.delete()
            return JsonResponse({'success': True, 'message': 'You have successfully unfollowed ' + username})
        Follow.objects.create(follower_id=request.user, following_id=user)
        return JsonResponse({'success': True, 'message': 'You have successfully followed ' + username})

    except(ObjectDoesNotExist, FieldDoesNotExist):
        return JsonResponse({'success': False, 'message': 'The user you tried to follow was not found'})


def get_followers(request, username):
    """
    Get the users following the given user

    :param request: The request that called this function
    :param username: The user to get the followers for
    :return: list of followers or failure message in JSON format
    """
    try:
        user = User.objects.get(username=username)
        followers = Follow.objects.filter(following_id=user).values('follower_id', 'following_id')
        return JsonResponse(list(followers), safe=False)
    except(ObjectDoesNotExist, FieldDoesNotExist):
        messages.error(request, 'The given username was not found', extra_tags='danger')
        return JsonResponse({'success': False, 'message': 'The given username was not found'})


def get_following(request, username):
    """
    Get the users followed by the given user

    :param request: The request that called this function
    :param username: The user to get the followers for
    :return: list of followers or failure message in JSON format
    """
    try:
        user = User.objects.get(username=username)
        followers = Follow.objects.filter(follower_id=user).values('follower_id', 'following_id')
        return JsonResponse(list(followers), safe=False)
    except(ObjectDoesNotExist, FieldDoesNotExist):
        messages.error(request, 'The given username was not found', extra_tags='danger')
        return JsonResponse({'success': False, 'message': 'The given username was not found'})


def get_user_ids(request, user_ids):
    """
    Get the users with the given IDs in JSON format

    :param request: The request that called this function
    :param user_ids: The user ids to get the users for
    :return: list of users in JSON format
    """
    user_ids_list = filter(bool, user_ids.split('/'))
    user_ids_list = list(map(int, user_ids_list))
    users = User.objects.filter(pk__in=user_ids_list).values('username')
    return JsonResponse(list(users), safe=False)


def get_user_id(request, user_id):
    """
    Get the user with the given ID in JSON format

    :param request: The request that called this function
    :param user_id: The user id
    :return: user in JSON format
    """
    print(user_id)
    users = User.objects.filter(pk=user_id).values('username')
    return JsonResponse(list(users), safe=False)
