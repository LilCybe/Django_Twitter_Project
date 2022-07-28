from rest_framework.test import APIClient
from testing.testcases import TestCase
from accounts.models import UserProfile


LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'


class AccountApiTests(TestCase):

    def setUp(self):
        # this function will be run at each test function is executed
        self.client = APIClient()
        self.user = self.create_user(
            username='admin',
            email='admin@jiuzhang.com',
            password='correct password',
        )

    def test_login(self):
        # every function must start with test_ to be automatically executed
        # must use post not get
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # login fail，http status code return 405 = METHOD_NOT_ALLOWED
        self.assertEqual(response.status_code, 405)
        # used post but wrong password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)
        # varified but not login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)
        # correct password
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@jiuzhang.com')
        # varified and logined
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    def test_logout(self):
        # login
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        # test whether the user is login
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)
        # test must use post
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)
        # use post success logout
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)
        # verified the user is logout
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        }
        # test get failed
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # test wrong email
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)
        # test too short password
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': '123',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)
        # test too long passowrd
        response = self.client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooooooo loooooooong',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)
        # successfully register
        response = self.client.post(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')
        # verify user profile is created
        created_user_id = response.data['user']['id']
        profile = UserProfile.objects.filter(user_id=created_user_id).first()
        self.assertNotEqual(profile, None)
        # verify use is logged in
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)
