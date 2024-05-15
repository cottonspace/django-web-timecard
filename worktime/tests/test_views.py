from django.contrib.auth.models import User
from django.test import TestCase


class TestNotLoggedInView(TestCase):
    def test_not_logged_in_login_status_code(self):
        response = self.client.get('/worktime/login/')
        self.assertEqual(response.status_code, 200)

    def test_not_logged_in_password_change_redirect(self):
        response = self.client.get('/worktime/password_change/')
        self.assertRedirects(
            response,
            '/worktime/login/?next=/worktime/password_change/'
        )

    def test_not_logged_in_time_off_status_redirect(self):
        response = self.client.get('/worktime/time_off/status/')
        self.assertRedirects(
            response,
            '/worktime/login/?next=/worktime/time_off/status/'
        )

    def test_not_logged_in_time_off_request_redirect(self):
        response = self.client.get('/worktime/time_off/request/')
        self.assertRedirects(
            response,
            '/worktime/login/?next=/worktime/time_off/request/'
        )

    def test_not_logged_in_time_off_list_redirect(self):
        response = self.client.get('/worktime/time_off/list/')
        self.assertRedirects(
            response,
            '/worktime/login/?next=/worktime/time_off/list/'
        )

    def test_not_logged_in_time_off_accept_redirect(self):
        response = self.client.get('/worktime/time_off/accept/')
        self.assertRedirects(
            response,
            '/worktime/login/?next=/worktime/time_off/accept/'
        )

    def test_not_logged_in_time_off_cancel_redirect(self):
        response = self.client.get('/worktime/time_off/cancel/')
        self.assertRedirects(
            response,
            '/worktime/login/?next=/worktime/time_off/cancel/'
        )

    def test_not_logged_in_record_redirect(self):
        response = self.client.get('/worktime/record/')
        self.assertRedirects(
            response,
            '/worktime/login/?next=/worktime/record/'
        )

    def test_not_logged_in_record_calendar_redirect(self):
        response = self.client.get('/worktime/record/calendar/')
        self.assertRedirects(
            response,
            '/worktime/login/?next=/worktime/record/calendar/'
        )

    def test_not_logged_in_record_summary_redirect(self):
        response = self.client.get('/worktime/record/summary/')
        self.assertRedirects(
            response,
            '/worktime/login/?next=/worktime/record/summary/'
        )

    def test_not_logged_in_readme_status_code(self):
        response = self.client.get('/worktime/readme/')
        self.assertEqual(response.status_code, 200)


class TestUserLoggedInView(TestCase):
    def setUp(self):
        user = User.objects.create(
            username='user01', password='12345678', email='user01@example.com'
        )
        self.client.force_login(user)

    def test_user_login_redirect(self):
        response = self.client.get('/worktime/login/')
        self.assertRedirects(response, '/worktime/record/')

    def test_user_password_change_status_code(self):
        response = self.client.get('/worktime/password_change/')
        self.assertEqual(response.status_code, 200)

    def test_user_time_off_status_status_code(self):
        response = self.client.get('/worktime/time_off/status/')
        self.assertEqual(response.status_code, 403)

    def test_user_time_off_request_status_code(self):
        response = self.client.get('/worktime/time_off/request/')
        self.assertEqual(response.status_code, 200)

    def test_user_time_off_list_status_code(self):
        response = self.client.get('/worktime/time_off/list/')
        self.assertEqual(response.status_code, 403)

    def test_user_time_off_accept_redirect(self):
        response = self.client.get('/worktime/time_off/accept/')
        self.assertRedirects(
            response,
            '/worktime/time_off/list/',
            fetch_redirect_response=False
        )

    def test_user_time_off_cancel_redirect(self):
        response = self.client.get('/worktime/time_off/cancel/')
        self.assertRedirects(
            response,
            '/worktime/time_off/request/',
            fetch_redirect_response=False
        )

    def test_user_record_status_code(self):
        response = self.client.get('/worktime/record/')
        self.assertEqual(response.status_code, 200)

    def test_user_record_calendar_status_code(self):
        response = self.client.get('/worktime/record/calendar/')
        self.assertEqual(response.status_code, 200)

    def test_user_record_summary_status_code(self):
        response = self.client.get('/worktime/record/summary/')
        self.assertEqual(response.status_code, 403)

    def test_user_readme_status_code(self):
        response = self.client.get('/worktime/readme/')
        self.assertEqual(response.status_code, 200)


class TestStaffLoggedInView(TestCase):
    def setUp(self):
        user = User.objects.create(
            username='staff01', password='12345678', email='staff01@example.com'
        )
        user.is_staff = True
        user.save()
        self.client.force_login(user)

    def test_staff_login_redirect(self):
        response = self.client.get('/worktime/login/')
        self.assertRedirects(response, '/worktime/record/')

    def test_staff_password_change_status_code(self):
        response = self.client.get('/worktime/password_change/')
        self.assertEqual(response.status_code, 200)

    def test_staff_time_off_status_status_code(self):
        response = self.client.get('/worktime/time_off/status/')
        self.assertEqual(response.status_code, 200)

    def test_staff_time_off_request_status_code(self):
        response = self.client.get('/worktime/time_off/request/')
        self.assertEqual(response.status_code, 200)

    def test_staff_time_off_list_status_code(self):
        response = self.client.get('/worktime/time_off/list/')
        self.assertEqual(response.status_code, 200)

    def test_staff_time_off_accept_redirect(self):
        response = self.client.get('/worktime/time_off/accept/')
        self.assertRedirects(
            response,
            '/worktime/time_off/list/',
            fetch_redirect_response=False
        )

    def test_staff_time_off_cancel_redirect(self):
        response = self.client.get('/worktime/time_off/cancel/')
        self.assertRedirects(
            response,
            '/worktime/time_off/request/',
            fetch_redirect_response=False
        )

    def test_staff_record_status_code(self):
        response = self.client.get('/worktime/record/')
        self.assertEqual(response.status_code, 200)

    def test_staff_record_calendar_status_code(self):
        response = self.client.get('/worktime/record/calendar/')
        self.assertEqual(response.status_code, 200)

    def test_staff_record_summary_status_code(self):
        response = self.client.get('/worktime/record/summary/')
        self.assertEqual(response.status_code, 200)

    def test_staff_readme_status_code(self):
        response = self.client.get('/worktime/readme/')
        self.assertEqual(response.status_code, 200)


class TestStaffAndSuperUserLoggedInView(TestCase):
    def setUp(self):
        user = User.objects.create(
            username='superuser01', password='12345678', email='superuser01@example.com'
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        self.client.force_login(user)

    def test_superuser_login_redirect(self):
        response = self.client.get('/worktime/login/')
        self.assertRedirects(response, '/worktime/record/')

    def test_superuser_password_change_status_code(self):
        response = self.client.get('/worktime/password_change/')
        self.assertEqual(response.status_code, 200)

    def test_superuser_time_off_status_status_code(self):
        response = self.client.get('/worktime/time_off/status/')
        self.assertEqual(response.status_code, 200)

    def test_superuser_time_off_request_status_code(self):
        response = self.client.get('/worktime/time_off/request/')
        self.assertEqual(response.status_code, 200)

    def test_superuser_time_off_list_status_code(self):
        response = self.client.get('/worktime/time_off/list/')
        self.assertEqual(response.status_code, 200)

    def test_superuser_time_off_accept_redirect(self):
        response = self.client.get('/worktime/time_off/accept/')
        self.assertRedirects(
            response,
            '/worktime/time_off/list/',
            fetch_redirect_response=False
        )

    def test_superuser_time_off_cancel_redirect(self):
        response = self.client.get('/worktime/time_off/cancel/')
        self.assertRedirects(
            response,
            '/worktime/time_off/request/',
            fetch_redirect_response=False
        )

    def test_superuser_record_status_code(self):
        response = self.client.get('/worktime/record/')
        self.assertEqual(response.status_code, 200)

    def test_superuser_record_calendar_status_code(self):
        response = self.client.get('/worktime/record/calendar/')
        self.assertEqual(response.status_code, 200)

    def test_superuser_record_summary_status_code(self):
        response = self.client.get('/worktime/record/summary/')
        self.assertEqual(response.status_code, 200)

    def test_superuser_readme_status_code(self):
        response = self.client.get('/worktime/readme/')
        self.assertEqual(response.status_code, 200)
