from django.test import TestCase
from django.test import TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from wire_profile.models import Follow, Message


class RegisterViewTests(TransactionTestCase):
    """
    Test the sign up view
    """

    def test_create_account_no_input(self):
        """
        If no data is input, a valid message is displayed and the user is redirected to the sign up form
        """
        response = self.client.get(reverse('base:register'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:signup'))
        messages = list(response.context.get('messages'))
        self.assertEqual(len(messages), 3)
        for message in messages:
            self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(messages[0]), 'Please enter a username')
        self.assertEqual(str(messages[1]), 'Please enter a password')
        self.assertEqual(str(messages[2]), 'Please enter an email address')

    def test_create_account_valid_input(self):
        """
        Create an account using a post request with all input data being valid. A redirect to home should occur with
        a success message
        """
        response = self.client.post(reverse('base:register'), {'username': 'test', 'password': 'test', 'email': 'test@test.com'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:home'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(str(message), 'Welcome to Wire, test')

    def test_create_account_duplicate_usernames(self):
        """
        Try to create an account with two usernames. The second account should not be created
        """
        response1 = self.client.post(reverse('base:register'), {'username': 'test', 'password': 'test', 'email': 'test@test.com'}, follow=True)
        self.assertEqual(response1.status_code, 200)
        self.assertRedirects(response1, reverse('base:home'))
        message = list(response1.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(str(message), 'Welcome to Wire, test')

        response2 = self.client.post(reverse('base:register'), {'username': 'test', 'password': 'test', 'email': 'test@test.com'}, follow=True)
        self.assertEqual(response2.status_code, 200)
        self.assertRedirects(response2, reverse('base:signup'))
        message = list(response2.context.get('messages'))[0]
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'That username already exists')

    def test_create_account_invalid_email(self):
        """
        Try to create an account with an invalid email address. Should not be possible for normal users if front end
        validation is working but this test will ensure the backend validation works as a backup
        """
        response = self.client.post(reverse('base:register'), {'username': 'test', 'password': 'test', 'email': 'test'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:signup'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'Please enter a valid email address')

    def test_create_account_150_char_username(self):
        """
        Try to create an account with a username that is 150 characters long, the max length for a username.
        The account should be created successfully
        """
        username = 'AnWwD0jq7MnVUMaZOFBK8NYfdMXGLAplAUQUgy4Pp1ZCpSdlG25o259RghvLfwvbljbhfOK54ezspwOR8iB6Bh8rX60lHPfEjr5lScqfMJpUEhCq61QjRKnOAD77m0GsffeMK1gCHDA8g392sJHLtF'
        response = self.client.post(reverse('base:register'), {'username': username, 'password': 'test', 'email': 'test@test.com'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:home'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(str(message), 'Welcome to Wire, ' + username)

    def test_create_account_151_char_username(self):
        """
        Try to create an account with a username that is 151 characters long. This should fail because the maximum
        characters allowed for a username is 150.
        """
        username = 'UCrp5ZRHrfCCKVTjkyc8U1WY6DaD0gr4rFiYdPj9WMzKt8UiF7DFdyFfrMHOYn6Ve3j7b7i6jeMDT1HxTq4wuNP59U7qIv1dTYwdN2gn6XeoRBeMf1exeaZ7hkhbrTKoDrMU36kQ3t0RW8UNw2USpxL'
        response = self.client.post(reverse('base:register'), {'username': username, 'password': 'test', 'email': 'test@test.com'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:signup'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'The maximum number of characters for a username is 150')

    def test_create_account_254_char_email(self):
        """
        Try to create an account with an email addresss that is 254 characters long, the max length for an email.
        The account should be created successfully
        """
        email = 'XEFPOc1D79H5YtU4dbNGMVkFW6LqtvDGfGrbQp5TClemP3mkSGOuf7hc2xJif7iyHo6PaPunzJ5gyXXKK5eTLU392Y4dqDz1v3HzvuZSRhgiuhvMylUTCPtDoO6psuzx6p57yvUipkW6mDgbBsIVMjYYihz0092u2oyHSHa0cnFGJa8k07HBCo9L2qHQEukWyawzlHLgk5cxKjOq0jeG8RcSZGOvjXbw3iBIPHpKBpCE3T7XcBkOU@test.com'
        response = self.client.post(reverse('base:register'), {'username': 'test', 'password': 'test', 'email': email}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:home'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(str(message), 'Welcome to Wire, test')

    def test_create_account_254_char_inavlid_email(self):
        """
        Try to create an account with an invalid email addresss that is 254 characters long. The invalid email should
        be caught by the email validator and the program should redirect to the sign in page with an error message
        """
        email = 'XEFPOc1D79H5YtU4dbNGMVkFW6LqtvDGfGrbQp5TClemP3mkSGOuf7hc2xJif7iyHo6PaPunzJ5gyXXKK5eTLU392Y4dqDz1v3HzvuZSRhgiuhvMylUTCPtDoO6psuzx6p57yvUipkW6mDgbBsIVMjYYihz0092u2oyHSHa0cnFGJa8k07HBCo9L2qHQEukWyawzlHLgk5cxKjOq0jeG8RcSZGOvjXbw3iBIPHpKBpCE3T7XcBkOU3S2e5hCoV'
        response = self.client.post(reverse('base:register'), {'username': 'test', 'password': 'test', 'email': email}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:signup'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'Please enter a valid email address')

    def test_create_account_255_char_email(self):
        """
        Try to create an account with an email addresss that is 255 characters long. This should fail because the
        maximum characters allowed for an email address is 254.
        """
        email = 'XEFPOc1D79H5YtU4dbNGMVkFW6LqtvDGfGrbQp5TClemP3mkSGOuf7hc2xJif7iyHo6PaPunzJ5gyXXKK5eTLU392Y4dqDz1v3HzvuZSRhgiuhvMylUTCPtDoO6psuzx6p57yvUipkW6mDgbBsIVMjYYihz0092u2oyHSHa0cnFGJa8k07HBCo9L2qHQEukWyawzlHLgk5cxKjOq0jeG8RcSZGOvjXbw3iBIPHpKBpCE3T7XcBkOU@test.com'
        response = self.client.post(reverse('base:register'), {'username': 'test', 'password': 'test', 'email': email}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:home'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(str(message), 'Welcome to Wire, test')

    def test_create_account_1000_char_password(self):
        """
        Try to create an account with a password that is 1000 characters long. This should pass because passwords do
        not have a maximum number of characters.
        """
        password = 'u6hAi19KnedG8wjLP1vu7KMXUh5gEhNHilTZQfDMyxHbT65eiH5gb6Vg1EzGEWn8NNexnohz7Wia9XjZPUVD802cJjXMMCyi77W4uxv5U2PUvJfawul3KC3BCZBR7o9cD8V3Se1IN2V3RTT9y3LHNhCLwNjAunO0IMGrV9TP87KPar8LHHMAlDeJm9UU4zbNT4crzGvfIqRHZAD9HSqrgAmWXFb4luVEzCfrY4bEySn0t9tSZwiOCU6RwRkqAzoQEPPkU5ymF9ojgLrQe98TFB1x9geIxPvB94QW0NAst6IGV4M1F88ETtLs1YX2N6sV1g9sXLKSq9KfJsBiACXhKNwOxZfaQzDOxCTfpGma5pOrjsNhgLOsXzUxMhZMddJ89nMzXvKBmppymx8eG8mQMdumT61JYj9EoLRDo808BVlnb8rvmcSe8kyRNee1Ks0NVS1H00TyjcOVa6yPKxchFngloA9uH2yKPQzms8R81qh0PsXhkOiIsLuFBWCa1o84N0mi6of6H7y8zRvK7sLBkWN7inid5wWogvMbvHFTuCwwEgr9SvN5YmvsWjnA5kG7O2cIpo7PAAg8Kre5K8oZGVKPhZoMhWri5Llwisn9keFGn35a8j64jalRtJwTjoyiAGbULvtuxIjrSjbXwyIamH5gCKWir2rDgCdAGhPkBhtCIRuO2j2AIWpJCY5U8c01JbmscG0I0Kb6BGuGPmFm62BD4vdMsE4ACsRvu2X5hd6NEElUikTgFPEaOSVjvTtYF3GBXtos59yqsdA4cnqV5dDB2KsJH61wI0Q9weEIyqYwyhRdWp1C02GZt5aBbuvDPOEbNxAVOzxVuB06kf75uIXx3rqwSs0vYlxfpRHe8m6A6l9qboqzJ65IIekvyvkYMMGF5srGi5ZfS5jKsCDFrKHX56bajlDom2Imx1k4kwTChLMGpAuN2wHgnScKImWwtLhvLlWHsbw15hNpenH1ebVZjaPQaYQIHayyMQ8I'
        response = self.client.post(reverse('base:register'), {'username': 'test', 'password': password, 'email': 'test@test.com'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:home'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(str(message), 'Welcome to Wire, test')


class VerifyUserViewTests(TestCase):

    def test_valid_log_in(self):
        """
        Create a valid account and then try to log in to it
        """
        self.client.post(reverse('base:register'), {'username': 'test', 'password': 'test', 'email': 'test@test.com'})
        response = self.client.post(reverse('base:verify'), {'username': 'test', 'password': 'test'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:home'))
        # The first message here will be the new user welcome message, we want the second message
        message = list(response.context.get('messages'))[1]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(str(message), 'Welcome back, test')

    def test_nonexistent_user_log_in(self):
        response = self.client.post(reverse('base:verify'), {'username': 'test', 'password': 'test'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:login'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'Your username or password is incorrect')

    def test_empty_username_log_in(self):
        """
        Try to log in with an empty username. This should fail immediately, redirecting to the login page
        with an appropriate message.
        :return:
        """
        response = self.client.post(reverse('base:verify'), {'username': '', 'password': 'test'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:login'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'Please enter a username')

    def test_150_char_username_log_in(self):
        """
        Log in to an account with a username that is 150 characters long, the max length allowed. This should pass.
        """
        username = 'AnWwD0jq7MnVUMaZOFBK8NYfdMXGLAplAUQUgy4Pp1ZCpSdlG25o259RghvLfwvbljbhfOK54ezspwOR8iB6Bh8rX60lHPfEjr5lScqfMJpUEhCq61QjRKnOAD77m0GsffeMK1gCHDA8g392sJHLtF'
        self.client.post(reverse('base:register'), {'username': username, 'password': 'test', 'email': 'test@test.com'})
        response = self.client.post(reverse('base:verify'), {'username': username, 'password': 'test'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:home'))
        # The first message here will be the new user welcome message, we want the second message
        message = list(response.context.get('messages'))[1]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(str(message), 'Welcome back, ' + username)

    def test_151_char_username_log_in(self):
        """
        Try to log in using a 151 character username. This should fail immediately due to the username being over
        the maximum number of characters allowed (150). The program should then redirect to the login page with
        an appropriate message
        """
        username = '1AnWwD0jq7MnVUMaZOFBK8NYfdMXGLAplAUQUgy4Pp1ZCpSdlG25o259RghvLfwvbljbhfOK54ezspwOR8iB6Bh8rX60lHPfEjr5lScqfMJpUEhCq61QjRKnOAD77m0GsffeMK1gCHDA8g392sJHLtF'
        response = self.client.post(reverse('base:verify'), {'username': username, 'password': 'test'}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:login'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'The maximum number of characters for a username is 150')

    def test_empty_password_log_in(self):
        """
        Try to log in with an empty password. This should fail immediately, redirecting to the login page
        with an appropriate message.
        :return:
        """
        response = self.client.post(reverse('base:verify'), {'username': 'test', 'password': ''}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:login'))
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, 'danger error')
        self.assertEqual(str(message), 'Please enter a password')

    def test_1000_char_password_log_in(self):
        """
        Log in to an account with a password that is 1000 characters long. Passwords have no max length so this should
        pass
        """
        password = 'u6hAi19KnedG8wjLP1vu7KMXUh5gEhNHilTZQfDMyxHbT65eiH5gb6Vg1EzGEWn8NNexnohz7Wia9XjZPUVD802cJjXMMCyi77W4uxv5U2PUvJfawul3KC3BCZBR7o9cD8V3Se1IN2V3RTT9y3LHNhCLwNjAunO0IMGrV9TP87KPar8LHHMAlDeJm9UU4zbNT4crzGvfIqRHZAD9HSqrgAmWXFb4luVEzCfrY4bEySn0t9tSZwiOCU6RwRkqAzoQEPPkU5ymF9ojgLrQe98TFB1x9geIxPvB94QW0NAst6IGV4M1F88ETtLs1YX2N6sV1g9sXLKSq9KfJsBiACXhKNwOxZfaQzDOxCTfpGma5pOrjsNhgLOsXzUxMhZMddJ89nMzXvKBmppymx8eG8mQMdumT61JYj9EoLRDo808BVlnb8rvmcSe8kyRNee1Ks0NVS1H00TyjcOVa6yPKxchFngloA9uH2yKPQzms8R81qh0PsXhkOiIsLuFBWCa1o84N0mi6of6H7y8zRvK7sLBkWN7inid5wWogvMbvHFTuCwwEgr9SvN5YmvsWjnA5kG7O2cIpo7PAAg8Kre5K8oZGVKPhZoMhWri5Llwisn9keFGn35a8j64jalRtJwTjoyiAGbULvtuxIjrSjbXwyIamH5gCKWir2rDgCdAGhPkBhtCIRuO2j2AIWpJCY5U8c01JbmscG0I0Kb6BGuGPmFm62BD4vdMsE4ACsRvu2X5hd6NEElUikTgFPEaOSVjvTtYF3GBXtos59yqsdA4cnqV5dDB2KsJH61wI0Q9weEIyqYwyhRdWp1C02GZt5aBbuvDPOEbNxAVOzxVuB06kf75uIXx3rqwSs0vYlxfpRHe8m6A6l9qboqzJ65IIekvyvkYMMGF5srGi5ZfS5jKsCDFrKHX56bajlDom2Imx1k4kwTChLMGpAuN2wHgnScKImWwtLhvLlWHsbw15hNpenH1ebVZjaPQaYQIHayyMQ8I'
        self.client.post(reverse('base:register'), {'username': 'test', 'password': password, 'email': 'test@test.com'})
        response = self.client.post(reverse('base:verify'), {'username': 'test', 'password': password}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:home'))
        # The first message here will be the new user welcome message, we want the second message
        message = list(response.context.get('messages'))[1]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(str(message), 'Welcome back, test')


class LogOutViewTest(TestCase):

    def test_log_out(self):
        """
        Log out of an account that the test has created and logged in to
        """
        self.client.post(reverse('base:register'), {'username': 'test', 'password': 'test', 'email': 'test@test.com'})
        self.client.post(reverse('base:verify'), {'username': 'test', 'password': 'test'})
        response = self.client.get(reverse('base:logout'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, reverse('base:home'))
        # The first and second messages here will be the sign up and log in messages, we want the third message.
        message = list(response.context.get('messages'))[2]
        self.assertEqual(message.tags, 'success')
        self.assertEqual(str(message), 'You have logged out successfully')


class RecommendedUsersViewTest(TestCase):
    def test_get_recommended_users_while_logged_in(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')
        User.objects.create_user('test2', 'test2@test.com', 'test')
        User.objects.create_user('test3', 'test3@test.com', 'test')

        self.client.post(reverse('base:verify'), {'username': user.username, 'password': 'test'})
        url = reverse('base:recommended_users', kwargs={'excluded_username': user.username})

        response = self.client.get(url)
        response_content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('testfoo', response_content)
        self.assertIn('test2', response_content)
        self.assertIn('test3', response_content)

    def test_get_recommended_users_while_logged_in_and_excluding_another_user(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')
        user2 = User.objects.create_user('test2', 'test2@test.com', 'test')
        User.objects.create_user('test3', 'test3@test.com', 'test')
        User.objects.create_user('test4', 'test4@test.com', 'test')
        User.objects.create_user('test5', 'test5@test.com', 'test')

        self.client.post(reverse('base:verify'), {'username': user.username, 'password': 'test'})
        url = reverse('base:recommended_users', kwargs={'excluded_username': user2.username})

        response = self.client.get(url)
        response_content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('testfoo', response_content)
        self.assertNotIn('test2', response_content)
        self.assertIn('test3', response_content)

    def test_get_maximum_of_five_recommended_users(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')
        User.objects.create_user('test2', 'test2@test.com', 'test')
        User.objects.create_user('test3', 'test3@test.com', 'test')
        User.objects.create_user('test4', 'test4@test.com', 'test')
        User.objects.create_user('test5', 'test5@test.com', 'test')
        User.objects.create_user('test6', 'test6@test.com', 'test')
        User.objects.create_user('test7', 'test7@test.com', 'test')

        self.client.post(reverse('base:verify'), {'username': user.username, 'password': 'test'})
        url = reverse('base:recommended_users', kwargs={'excluded_username': user.username})

        response = self.client.get(url)
        response_content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('testfoo', response_content)
        self.assertIn('test2', response_content)
        self.assertIn('test3', response_content)
        self.assertIn('test4', response_content)
        self.assertIn('test5', response_content)
        self.assertIn('test6', response_content)
        self.assertNotIn('test7', response_content)

    def test_exclusing_of_one_followed_user(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')
        user2 = User.objects.create_user('test2', 'test2@test.com', 'test')
        User.objects.create_user('test3', 'test3@test.com', 'test')
        User.objects.create_user('test4', 'test4@test.com', 'test')
        User.objects.create_user('test5', 'test5@test.com', 'test')
        User.objects.create_user('test6', 'test6@test.com', 'test')
        User.objects.create_user('test7', 'test7@test.com', 'test')
        User.objects.create_user('test8', 'test8@test.com', 'test')

        Follow.objects.create(follower_id=user, following_id=user2)

        self.client.post(reverse('base:verify'), {'username': user.username, 'password': 'test'})
        url = reverse('base:recommended_users', kwargs={'excluded_username': user.username})

        response = self.client.get(url)
        response_content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('testfoo', response_content)
        self.assertNotIn('test2', response_content)
        self.assertIn('test3', response_content)
        self.assertIn('test4', response_content)
        self.assertIn('test5', response_content)
        self.assertIn('test6', response_content)
        self.assertIn('test7', response_content)
        self.assertNotIn('test8', response_content)

    def test_exclusion_of_multiple_followed_users(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')
        user2 = User.objects.create_user('test2', 'test2@test.com', 'test')
        user3 = User.objects.create_user('test3', 'test3@test.com', 'test')
        user4 = User.objects.create_user('test4', 'test4@test.com', 'test')
        User.objects.create_user('test5', 'test5@test.com', 'test')
        User.objects.create_user('test6', 'test6@test.com', 'test')
        User.objects.create_user('test7', 'test7@test.com', 'test')
        User.objects.create_user('test8', 'test8@test.com', 'test')
        User.objects.create_user('test9', 'test9@test.com', 'test')
        User.objects.create_user('test10', 'test10@test.com', 'test')

        Follow.objects.create(follower_id=user, following_id=user2)
        Follow.objects.create(follower_id=user, following_id=user3)
        Follow.objects.create(follower_id=user, following_id=user4)

        self.client.post(reverse('base:verify'), {'username': user.username, 'password': 'test'})
        url = reverse('base:recommended_users', kwargs={'excluded_username': user.username})

        response = self.client.get(url)
        response_content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('testfoo', response_content)
        self.assertNotIn('test2', response_content)
        self.assertNotIn('test3', response_content)
        self.assertNotIn('test4', response_content)
        self.assertIn('test5', response_content)
        self.assertIn('test6', response_content)
        self.assertIn('test7', response_content)
        self.assertIn('test8', response_content)
        self.assertIn('test9', response_content)
        self.assertNotIn('test10', response_content)

    def test_response_when_no_other_users(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')

        self.client.post(reverse('base:verify'), {'username': user.username, 'password': 'test'})
        url = reverse('base:recommended_users', kwargs={'excluded_username': user.username})

        response = self.client.get(url)
        response_content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('testfoo', response_content)

    def test_response_when_every_user_is_being_followed(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')
        user2 = User.objects.create_user('test2', 'test2@test.com', 'test')
        user3 = User.objects.create_user('test3', 'test3@test.com', 'test')
        user4 = User.objects.create_user('test4', 'test4@test.com', 'test')
        user5 = User.objects.create_user('test5', 'test5@test.com', 'test')
        user6 = User.objects.create_user('test6', 'test6@test.com', 'test')
        user7 = User.objects.create_user('test7', 'test7@test.com', 'test')

        Follow.objects.create(follower_id=user, following_id=user2)
        Follow.objects.create(follower_id=user, following_id=user3)
        Follow.objects.create(follower_id=user, following_id=user4)
        Follow.objects.create(follower_id=user, following_id=user5)
        Follow.objects.create(follower_id=user, following_id=user6)
        Follow.objects.create(follower_id=user, following_id=user7)

        self.client.post(reverse('base:verify'), {'username': user.username, 'password': 'test'})
        url = reverse('base:recommended_users', kwargs={'excluded_username': user.username})

        response = self.client.get(url)
        response_content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('testfoo', response_content)
        self.assertNotIn('test2', response_content)
        self.assertNotIn('test3', response_content)
        self.assertNotIn('test4', response_content)
        self.assertNotIn('test5', response_content)
        self.assertNotIn('test6', response_content)
        self.assertNotIn('test7', response_content)


class HomeViewTest(TestCase):
    def test_correct_template_loaded(self):
        response = self.client.get(reverse('base:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('base/index.html')

    def test_five_latest_normal_messages_loaded(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')

        Message.objects.create(message_text='foo', created=timezone.now(), user=user)
        Message.objects.create(message_text='bar', created=timezone.now(), user=user)
        Message.objects.create(message_text='baz', created=timezone.now(), user=user)
        Message.objects.create(message_text='bam', created=timezone.now(), user=user)
        Message.objects.create(message_text='fam', created=timezone.now(), user=user)
        Message.objects.create(message_text='tam', created=timezone.now(), user=user)
        Message.objects.create(message_text='lam', created=timezone.now(), user=user)

        response = self.client.get(reverse('base:home'))
        latest_messages = response.context['latest_messages']
        messages = [message.message_text for message in latest_messages]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(messages), 5)
        self.assertNotIn('foo', messages)
        self.assertNotIn('bar', messages)
        self.assertIn('baz', messages)
        self.assertIn('bam', messages)
        self.assertIn('fam', messages)
        self.assertIn('tam', messages)
        self.assertIn('lam', messages)

    def test_five_latest_tagged_messages_loaded(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')

        Message.objects.create(message_text='hello #foo', created=timezone.now(), user=user)
        Message.objects.create(message_text='hello #bar', created=timezone.now(), user=user)
        Message.objects.create(message_text='hello #baz', created=timezone.now(), user=user)
        Message.objects.create(message_text='hello #bam', created=timezone.now(), user=user)
        Message.objects.create(message_text='hello #fam', created=timezone.now(), user=user)
        Message.objects.create(message_text='hello #tam', created=timezone.now(), user=user)
        Message.objects.create(message_text='hello #lam', created=timezone.now(), user=user)

        response = self.client.get(reverse('base:home'))
        latest_tagged_messages = response.context['latest_tagged_messages']
        messages = [message.message_text for message in latest_tagged_messages]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(messages), 5)
        self.assertNotIn('hello #foo', messages)
        self.assertNotIn('hello #bar', messages)
        self.assertIn('hello #baz', messages)
        self.assertIn('hello #bam', messages)
        self.assertIn('hello #fam', messages)
        self.assertIn('hello #tam', messages)
        self.assertIn('hello #lam', messages)

    def test_one_normal_message_and_one_tagged_message_loaded(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')

        Message.objects.create(message_text='hello foo', created=timezone.now(), user=user)
        Message.objects.create(message_text='hello #bar', created=timezone.now(), user=user)

        response = self.client.get(reverse('base:home'))
        latest_messages = response.context['latest_messages']
        l_messages = [message.message_text for message in latest_messages]
        latest_tagged_messages = response.context['latest_tagged_messages']
        l_t_messages = [message.message_text for message in latest_tagged_messages]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(l_messages), 2)
        self.assertEqual(len(l_t_messages), 1)
        self.assertIn('hello foo', l_messages)
        self.assertIn('hello #bar', l_messages)
        self.assertIn('hello #bar', l_t_messages)
        self.assertNotIn('foo', l_t_messages)

    def test_five_normal_messages_and_five_tagged_messages_loaded(self):
        user = User.objects.create_user('testfoo', 'test@test.com', 'test')

        Message.objects.create(message_text='hello #foo', created=timezone.now(), user=user)
        Message.objects.create(message_text='hello #bar', created=timezone.now(), user=user)
        Message.objects.create(message_text='hello #baz', created=timezone.now(), user=user)
        Message.objects.create(message_text='hello #bam', created=timezone.now(), user=user)
        Message.objects.create(message_text='spam', created=timezone.now(), user=user)
        Message.objects.create(message_text='flam', created=timezone.now(), user=user)
        Message.objects.create(message_text='clam', created=timezone.now(), user=user)
        Message.objects.create(message_text='hello #fam', created=timezone.now(), user=user)
        Message.objects.create(message_text='hello #tam', created=timezone.now(), user=user)
        Message.objects.create(message_text='hello #lam', created=timezone.now(), user=user)
        Message.objects.create(message_text='slam', created=timezone.now(), user=user)

        response = self.client.get(reverse('base:home'))
        latest_messages = response.context['latest_messages']
        l_messages = [message.message_text for message in latest_messages]
        latest_tagged_messages = response.context['latest_tagged_messages']
        l_t_messages = [message.message_text for message in latest_tagged_messages]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(l_messages), 5)
        self.assertEqual(len(l_t_messages), 5)

        self.assertNotIn('hello #foo', l_messages)
        self.assertNotIn('hello #bar', l_messages)
        self.assertNotIn('hello #baz', l_messages)
        self.assertNotIn('hello #bam', l_messages)
        self.assertNotIn('spam', l_messages)
        self.assertNotIn('flam', l_messages)
        self.assertIn('clam', l_messages)
        self.assertIn('hello #fam', l_messages)
        self.assertIn('hello #tam', l_messages)
        self.assertIn('hello #lam', l_messages)
        self.assertIn('slam', l_messages)

        self.assertNotIn('hello #foo', l_t_messages)
        self.assertNotIn('hello #bar', l_t_messages)
        self.assertNotIn('spam', l_t_messages)
        self.assertNotIn('flam', l_t_messages)
        self.assertNotIn('clam', l_t_messages)
        self.assertNotIn('slam', l_t_messages)
        self.assertIn('hello #baz', l_t_messages)
        self.assertIn('hello #bam', l_t_messages)
        self.assertIn('hello #fam', l_t_messages)
        self.assertIn('hello #tam', l_t_messages)
        self.assertIn('hello #lam', l_t_messages)
