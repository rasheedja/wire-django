from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from .forms import NewWireForm, SearchForm
from .models import Message, Follow


class ProfileViewTest(TestCase):
    def test_profile_loaded_for_valid_user(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')

        response = self.client.get(reverse('wire_profile:profile', kwargs={'username': user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], user)
        self.assertTemplateUsed(response, 'wire_profile/profile.html')

    def test_redirect_for_invalid_user(self):
        response = self.client.get(reverse('wire_profile:profile', kwargs={'username': 'foobar'}), follow=True)
        message = list(response.context['messages'])[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'The requested user was not found')
        self.assertTemplateUsed(response, 'wire_profile/search_user.html')


class CurrentProfileViewTest(TestCase):
    def test_access_when_not_logged_in(self):
        response = self.client.get(reverse('wire_profile:current_profile'), follow=True)
        message = list(response.context['messages'])[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'You must log in to view your profile page')

    def test_current_profile_page_for_logged_in_users(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')
        self.client.post(reverse('base:verify'), {'username': user.username, 'password': 'test'})
        response = self.client.get(reverse('wire_profile:current_profile'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], user)
        self.assertIsInstance(response.context['form'], NewWireForm)
        self.assertTemplateUsed(response, 'wire_profile/current_profile.html')


class SearchViewTest(TestCase):
    def test_search_form_and_template_rendered_correctly(self):
        response = self.client.get(reverse('wire_profile:search'))

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], SearchForm)
        self.assertTemplateUsed(response, 'wire_profile/search.html')

    def test_error_message_if_search_form_not_populated(self):
        response = self.client.post(reverse('wire_profile:search'))
        message = list(response.context['messages'])[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['form'].is_valid(), False)
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'Please complete the search form')
        self.assertTemplateUsed(response, 'wire_profile/search.html')

    def test_successful_user_search(self):
        response = self.client.post(reverse('wire_profile:search'),
                                    {'search_query': 'test', 'is_wire_search': 'false'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wire_profile/search_user.html')

    def test_successful_message_search(self):
        response = self.client.post(reverse('wire_profile:search'),
                                    {'search_query': 'test', 'is_wire_search': 'true'}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wire_profile/search_message.html')


class SearchMessageViewTest(TestCase):
    def test_message_view_template_rendered(self):
        response = self.client.get(reverse('wire_profile:search_message', kwargs={'query': 'test'}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wire_profile/search_message.html')

    def test_single_message_included_in_template(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')
        Message.objects.create(message_text='foo', created=timezone.now(), user=user)
        Message.objects.create(message_text='barbaz', created=timezone.now(), user=user)
        Message.objects.create(message_text='bazbar', created=timezone.now(), user=user)

        response = self.client.get(reverse('wire_profile:search_message', kwargs={'query': 'foo'}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wire_profile/search_message.html')
        self.assertIn('foo', response_content)
        self.assertNotIn('barbaz', response_content)
        self.assertNotIn('bazbar', response_content)

    def test_multiple_messages_included_in_template(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')
        Message.objects.create(message_text='foo', created=timezone.now(), user=user)
        Message.objects.create(message_text='foobar', created=timezone.now(), user=user)
        Message.objects.create(message_text='foobarfoo', created=timezone.now(), user=user)
        Message.objects.create(message_text='barbaz', created=timezone.now(), user=user)
        Message.objects.create(message_text='bazbar', created=timezone.now(), user=user)

        response = self.client.get(reverse('wire_profile:search_message', kwargs={'query': 'foo'}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wire_profile/search_message.html')
        self.assertIn('foo', response_content)
        self.assertIn('foobar', response_content)
        self.assertIn('foobarfoo', response_content)
        self.assertNotIn('barbaz', response_content)
        self.assertNotIn('bazbar', response_content)


class SearchUserViewTest(TestCase):
    def test_user_view_template_rendered(self):
        response = self.client.get(reverse('wire_profile:search_user', kwargs={'query': 'test'}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wire_profile/search_user.html')

    def test_single_user_included_in_template(self):
        User.objects.create_user('foo', 'test@test.com', 'test')
        User.objects.create_user('barbaz', 'test@test.com', 'test')
        User.objects.create_user('bazbar', 'test@test.com', 'test')

        response = self.client.get(reverse('wire_profile:search_user', kwargs={'query': 'foo'}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wire_profile/search_user.html')
        self.assertIn('foo', response_content)
        self.assertNotIn('barbaz', response_content)
        self.assertNotIn('bazbar', response_content)

    def test_multiple_users_included_in_template(self):
        User.objects.create_user('foo', 'test@test.com', 'test')
        User.objects.create_user('foobar', 'test@test.com', 'test')
        User.objects.create_user('foobarfoo', 'test@test.com', 'test')
        User.objects.create_user('barbaz', 'test@test.com', 'test')
        User.objects.create_user('bazbar', 'test@test.com', 'test')

        response = self.client.get(reverse('wire_profile:search_user', kwargs={'query': 'foo'}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wire_profile/search_user.html')
        self.assertIn('foo', response_content)
        self.assertIn('foobar', response_content)
        self.assertIn('foobarfoo', response_content)
        self.assertNotIn('barbaz', response_content)
        self.assertNotIn('bazbar', response_content)


class CreateMessageTest(TestCase):
    def test_no_access_for_get_requests(self):
        response = self.client.get(reverse('wire_profile:message'), follow=True)
        message = list(response.context['messages'])[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'Sorry, you cannot access that URL')

    def test_post_request_with_no_input(self):
        response = self.client.post(reverse('wire_profile:message'), follow=True)
        message = list(response.context['messages'])[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'Please enter a message')

    def test_post_request_when_not_logged_in(self):
        response = self.client.post(reverse('wire_profile:message'), {'message': 'test'}, follow=True)
        message = list(response.context['messages'])[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'Sorry, only registered users can create messages')

    def test_valid_post_request(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        self.client.post(reverse('base:verify'), {'username': user.username, 'password': 'test'})

        response = self.client.post(reverse('wire_profile:message'), {'message': 'test'}, follow=True)
        message = list(response.context['messages'])[1]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(message.tags, 'success success')
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.first().message_text, 'test')
        self.assertEqual(str(message), 'Message created successfully')


class GetMessagesTest(TestCase):
    def test_get_message_for_invalid_user(self):
        response = self.client.get(reverse('wire_profile:get_message', kwargs={'username': 'foo'}), follow=True)
        message = list(response.context['messages'])[0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'The requested user was not found')

    def test_get_message_with_no_messages(self):
        User.objects.create_user('foo', 'test@test.com', 'test')
        response = self.client.get(reverse('wire_profile:get_message', kwargs={'username': 'foo'}), follow=True)
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('The requested user was not found', response_content)

    def test_get_message_with_one_message(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('foo2', 'test2@test.com', 'test')
        Message.objects.create(message_text='barbar', created=timezone.now(), user=user)
        Message.objects.create(message_text='testtest', created=timezone.now(), user=user2)
        Message.objects.create(message_text='bazbaz', created=timezone.now(), user=user2)

        response = self.client.get(reverse('wire_profile:get_message', kwargs={'username': 'foo'}), follow=True)
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('barbar', response_content)
        self.assertNotIn('testtest', response_content)
        self.assertNotIn('bazbaz', response_content)

    def test_get_message_with_multiple_messages(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('foo2', 'test2@test.com', 'test')
        Message.objects.create(message_text='barbar', created=timezone.now(), user=user)
        Message.objects.create(message_text='testtest', created=timezone.now(), user=user)
        Message.objects.create(message_text='bazbaz', created=timezone.now(), user=user)
        Message.objects.create(message_text='bombom', created=timezone.now(), user=user2)
        Message.objects.create(message_text='bambam', created=timezone.now(), user=user2)

        response = self.client.get(reverse('wire_profile:get_message', kwargs={'username': 'foo'}), follow=True)
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('barbar', response_content)
        self.assertIn('testtest', response_content)
        self.assertIn('bazbaz', response_content)
        self.assertNotIn('bombom', response_content)
        self.assertNotIn('bambam', response_content)


class GetMessagesByIdsTest(TestCase):
    def test_get_messages_by_ids_for_invalid_ids(self):
        """
        This should just return an empty JSON object
        """
        response = self.client.get(reverse('wire_profile:get_messages_by_ids', kwargs={'user_ids': '1/2/3/4/5'}), follow=True)
        response_content = response.content.decode()

        self.assertNotIn('The requested users were not found', response_content)

    def test_get_messages_with_no_messages(self):
        User.objects.create_user('foo', 'test@test.com', 'test')
        response = self.client.get(reverse('wire_profile:get_messages_by_ids', kwargs={'user_ids': '1/2/3/4/5'}), follow=True)
        response_content = response.content.decode()

        self.assertNotIn('The requested users were not found', response_content)

    def test_get_message_for_one_user(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('foo2', 'test2@test.com', 'test')
        Message.objects.create(message_text='barbar', created=timezone.now(), user=user)
        Message.objects.create(message_text='testtest', created=timezone.now(), user=user2)
        Message.objects.create(message_text='bazbaz', created=timezone.now(), user=user2)

        response = self.client.get(reverse('wire_profile:get_messages_by_ids',
                                           kwargs={'user_ids': '' + str(user.id) + '/'}),
                                   follow=True)
        response_content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn('barbar', response_content)
        self.assertIn('"user": ' + str(user.id), response_content)
        self.assertNotIn('testtest', response_content)
        self.assertNotIn('bazbaz', response_content)
        self.assertNotIn('"user": ' + str(user2.id), response_content)

    def test_get_messages_for_multiple_user(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('foo2', 'test2@test.com', 'test')
        Message.objects.create(message_text='barbar', created=timezone.now(), user=user)
        Message.objects.create(message_text='testtest', created=timezone.now(), user=user2)
        Message.objects.create(message_text='bazbaz', created=timezone.now(), user=user2)

        response = self.client.get(reverse('wire_profile:get_messages_by_ids',
                                           kwargs={'user_ids': '' + str(user.id) + '/' + str(user2.id) + '/'}),
                                   follow=True)
        response_content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn('barbar', response_content)
        self.assertIn('"user": ' + str(user.id), response_content)
        self.assertIn('testtest', response_content)
        self.assertIn('bazbaz', response_content)
        self.assertIn('"user": ' + str(user2.id), response_content)

    def test_get_multiple_messages_for_one_user(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('foo2', 'test2@test.com', 'test')
        Message.objects.create(message_text='barbar', created=timezone.now(), user=user)
        Message.objects.create(message_text='testtest', created=timezone.now(), user=user)
        Message.objects.create(message_text='bazbaz', created=timezone.now(), user=user)
        Message.objects.create(message_text='bombom', created=timezone.now(), user=user2)
        Message.objects.create(message_text='bambam', created=timezone.now(), user=user2)

        response = self.client.get(reverse('wire_profile:get_messages_by_ids',
                                           kwargs={'user_ids': '' + str(user.id) + '/'}),
                                   follow=True)
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('barbar', response_content)
        self.assertIn('testtest', response_content)
        self.assertIn('bazbaz', response_content)
        self.assertIn('"user": ' + str(user.id), response_content)
        self.assertNotIn('bombom', response_content)
        self.assertNotIn('bambam', response_content)
        self.assertNotIn('"user": ' + str(user2.id), response_content)

    def test_get_multiple_messages_for_multiple_users(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('foo2', 'test2@test.com', 'test')
        Message.objects.create(message_text='barbar', created=timezone.now(), user=user)
        Message.objects.create(message_text='testtest', created=timezone.now(), user=user)
        Message.objects.create(message_text='bazbaz', created=timezone.now(), user=user)
        Message.objects.create(message_text='bombom', created=timezone.now(), user=user2)
        Message.objects.create(message_text='bambam', created=timezone.now(), user=user2)

        response = self.client.get(reverse('wire_profile:get_messages_by_ids',
                                           kwargs={'user_ids': '' + str(user.id) + '/' + str(user2.id) + '/'}),
                                   follow=True)
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('barbar', response_content)
        self.assertIn('testtest', response_content)
        self.assertIn('bazbaz', response_content)
        self.assertIn('"user": ' + str(user.id), response_content)
        self.assertIn('bombom', response_content)
        self.assertIn('bambam', response_content)
        self.assertIn('"user": ' + str(user2.id), response_content)


class FollowUserTest(TestCase):
    def test_unauthenticated_access_is_blocked(self):
        response = self.client.get(reverse('wire_profile:follow_user', kwargs={'username': 'test'}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('"success": false', response_content)
        self.assertIn('You must be logged in to follow a user', response_content)

    def test_self_following_is_prevented(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        self.client.post(reverse('base:verify'), {'username': user.username, 'password': 'test'})

        response = self.client.get(reverse('wire_profile:follow_user', kwargs={'username': user.username}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('"success": false', response_content)
        self.assertIn('You cannot follow yourself!', response_content)

    def test_follow_unknown_user(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        self.client.post(reverse('base:verify'), {'username': user.username, 'password': 'test'})

        response = self.client.get(reverse('wire_profile:follow_user', kwargs={'username': 'bar'}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('"success": false', response_content)
        self.assertIn('The user you tried to follow was not found', response_content)

    def test_follow_user(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('bar', 'bar@test.com', 'test')

        self.client.post(reverse('base:verify'), {'username': user.username, 'password': 'test'})

        response = self.client.get(reverse('wire_profile:follow_user', kwargs={'username': 'bar'}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('"success": true', response_content)
        self.assertIn('You have successfully followed bar', response_content)
        self.assertEqual(Follow.objects.count(), 1)

    def test_unfollow_user(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('bar', 'bar@test.com', 'test')

        self.client.post(reverse('base:verify'), {'username': user.username, 'password': 'test'})

        self.client.get(reverse('wire_profile:follow_user', kwargs={'username': 'bar'}))
        response = self.client.get(reverse('wire_profile:follow_user', kwargs={'username': 'bar'}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('"success": true', response_content)
        self.assertIn('You have successfully unfollowed bar', response_content)
        self.assertEqual(Follow.objects.count(), 0)


class GetFollowersTest(TestCase):
    def test_get_followers_unregistered_user(self):
        response = self.client.get(reverse('wire_profile:get_followers', kwargs={'username': 'test'}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('"success": false', response_content)
        self.assertIn('The given username was not found', response_content)

    def test_get_followers_valid_user(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')

        response = self.client.get(reverse('wire_profile:get_followers', kwargs={'username': user.username}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('"success": false', response_content)
        self.assertNotIn('The given username was not found', response_content)

    def test_get_followers_one_follower(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('bar', 'bar@test.com', 'test')
        user3 = User.objects.create_user('baz', 'baz@test.com', 'test')

        Follow.objects.create(follower_id=user2, following_id=user)

        response = self.client.get(reverse('wire_profile:get_followers', kwargs={'username': user.username}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('"following_id": ' + str(user.id), response_content)
        self.assertIn('"follower_id": ' + str(user2.id), response_content)
        self.assertNotIn('"following_id": ' + str(user2.id), response_content)
        self.assertNotIn('"follower_id": ' + str(user.id), response_content)
        self.assertNotIn('"following_id": ' + str(user3.id), response_content)
        self.assertNotIn('"follower_id": ' + str(user3.id), response_content)

    def test_get_followers_multiple_followers(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('bar', 'bar@test.com', 'test')
        user3 = User.objects.create_user('baz', 'baz@test.com', 'test')
        user4 = User.objects.create_user('boo', 'boo@test.com', 'test')
        user5 = User.objects.create_user('bam', 'bam@test.com', 'test')
        user6 = User.objects.create_user('fan', 'fan@test.com', 'test')

        Follow.objects.create(follower_id=user2, following_id=user)
        Follow.objects.create(follower_id=user3, following_id=user)
        Follow.objects.create(follower_id=user4, following_id=user)

        response = self.client.get(reverse('wire_profile:get_followers', kwargs={'username': user.username}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('"following_id": ' + str(user.id), response_content)
        self.assertIn('"follower_id": ' + str(user2.id), response_content)
        self.assertIn('"follower_id": ' + str(user3.id), response_content)
        self.assertIn('"follower_id": ' + str(user4.id), response_content)
        self.assertNotIn('"following_id": ' + str(user2.id), response_content)
        self.assertNotIn('"following_id": ' + str(user3.id), response_content)
        self.assertNotIn('"following_id": ' + str(user4.id), response_content)
        self.assertNotIn('"following_id": ' + str(user5.id), response_content)
        self.assertNotIn('"following_id": ' + str(user6.id), response_content)
        self.assertNotIn('"follower_id": ' + str(user.id), response_content)
        self.assertNotIn('"follower_id": ' + str(user5.id), response_content)
        self.assertNotIn('"follower_id": ' + str(user6.id), response_content)


class GetFollowingTest(TestCase):
    def test_get_following_unregistered_user(self):
        response = self.client.get(reverse('wire_profile:get_following', kwargs={'username': 'test'}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('"success": false', response_content)
        self.assertIn('The given username was not found', response_content)

    def test_get_following_valid_user(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')

        response = self.client.get(reverse('wire_profile:get_following', kwargs={'username': user.username}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('"success": false', response_content)
        self.assertNotIn('The given username was not found', response_content)

    def test_get_following_one_follower(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('bar', 'bar@test.com', 'test')
        user3 = User.objects.create_user('baz', 'baz@test.com', 'test')

        Follow.objects.create(follower_id=user, following_id=user2)

        response = self.client.get(reverse('wire_profile:get_following', kwargs={'username': user.username}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('"follower_id": ' + str(user.id), response_content)
        self.assertIn('"following_id": ' + str(user2.id), response_content)
        self.assertNotIn('"follower_id": ' + str(user2.id), response_content)
        self.assertNotIn('"following_id": ' + str(user.id), response_content)
        self.assertNotIn('"follower_id": ' + str(user3.id), response_content)
        self.assertNotIn('"following_id": ' + str(user3.id), response_content)

    def test_get_following_multiple_followers(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('bar', 'bar@test.com', 'test')
        user3 = User.objects.create_user('baz', 'baz@test.com', 'test')
        user4 = User.objects.create_user('boo', 'boo@test.com', 'test')
        user5 = User.objects.create_user('bam', 'bam@test.com', 'test')
        user6 = User.objects.create_user('fan', 'fan@test.com', 'test')

        Follow.objects.create(follower_id=user, following_id=user2)
        Follow.objects.create(follower_id=user, following_id=user3)
        Follow.objects.create(follower_id=user, following_id=user4)

        response = self.client.get(reverse('wire_profile:get_following', kwargs={'username': user.username}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('"follower_id": ' + str(user.id), response_content)
        self.assertIn('"following_id": ' + str(user2.id), response_content)
        self.assertIn('"following_id": ' + str(user3.id), response_content)
        self.assertIn('"following_id": ' + str(user4.id), response_content)
        self.assertNotIn('"follower_id": ' + str(user2.id), response_content)
        self.assertNotIn('"follower_id": ' + str(user3.id), response_content)
        self.assertNotIn('"follower_id": ' + str(user4.id), response_content)
        self.assertNotIn('"follower_id": ' + str(user5.id), response_content)
        self.assertNotIn('"follower_id": ' + str(user6.id), response_content)
        self.assertNotIn('"following_id": ' + str(user.id), response_content)
        self.assertNotIn('"following_id": ' + str(user5.id), response_content)
        self.assertNotIn('"following_id": ' + str(user6.id), response_content)


class GetUserIdsTest(TestCase):
    def test_get_user_ids_empty_path(self):
        response = self.client.get(reverse('wire_profile:get_user_ids', kwargs={'user_ids': '/'}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('username', response_content)

    def test_get_user_ids_invalid_user(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')

        response = self.client.get(reverse('wire_profile:get_user_ids', kwargs={'user_ids': str(user.id + 1) + '/'}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('username', response_content)

    def test_get_user_ids_one_user(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('bar', 'bar@test.com', 'test')
        user3 = User.objects.create_user('baz', 'baz@test.com', 'test')

        response = self.client.get(reverse('wire_profile:get_user_ids', kwargs={'user_ids': str(user.id) + '/'}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('"username": "' + user.username + '"', response_content)
        self.assertNotIn('"username": "' + user2.username + '"', response_content)
        self.assertNotIn('"username": "' + user3.username + '"', response_content)

    def test_get_user_ids_multiple_users(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('bar', 'bar@test.com', 'test')
        user3 = User.objects.create_user('baz', 'baz@test.com', 'test')
        user4 = User.objects.create_user('boo', 'boo@test.com', 'test')
        user5 = User.objects.create_user('bam', 'bam@test.com', 'test')
        user6 = User.objects.create_user('fan', 'fan@test.com', 'test')

        response = self.client.get(reverse('wire_profile:get_user_ids',
                                           kwargs=
                                           {'user_ids': str(user.id) + '/' + str(user2.id) + '/' + str(user3.id)}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('"username": "' + user.username + '"', response_content)
        self.assertIn('"username": "' + user2.username + '"', response_content)
        self.assertIn('"username": "' + user3.username + '"', response_content)
        self.assertNotIn('"username": "' + user4.username + '"', response_content)
        self.assertNotIn('"username": "' + user5.username + '"', response_content)
        self.assertNotIn('"username": "' + user6.username + '"', response_content)


class GetUserIdTest(TestCase):
    def test_get_user_id_empty_path(self):
        response = self.client.get(reverse('wire_profile:get_user_id', kwargs={'user_id': 0}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('username', response_content)

    def test_get_user_id_invalid_user(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')

        response = self.client.get(reverse('wire_profile:get_user_id', kwargs={'user_id': user.id + 1}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('username', response_content)

    def test_get_user_id_one_user(self):
        user = User.objects.create_user('foo', 'test@test.com', 'test')
        user2 = User.objects.create_user('bar', 'bar@test.com', 'test')
        user3 = User.objects.create_user('baz', 'baz@test.com', 'test')

        response = self.client.get(reverse('wire_profile:get_user_id', kwargs={'user_id': user.id}))
        response_content = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('"username": "' + user.username + '"', response_content)
        self.assertNotIn('"username": "' + user2.username + '"', response_content)
        self.assertNotIn('"username": "' + user3.username + '"', response_content)
