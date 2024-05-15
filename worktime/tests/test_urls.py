from django.test import TestCase
from django.urls import resolve, reverse

from worktime.views import (PasswordChange, ReadmeView, TimeOffListView,
                            TimeOffRequestView, TimeOffStatusView,
                            TimeRecordCalendarView, TimeRecordSummaryView,
                            TimeRecordView, UserLogin, UserLogout,
                            time_off_accept, time_off_cancel)


class TestUrls(TestCase):
    def test_login_url(self):
        self.assertEqual(
            resolve(reverse('worktime:login')).func.view_class,
            UserLogin
        )

    def test_logout_url(self):
        self.assertEqual(
            resolve(reverse('worktime:logout')).func.view_class,
            UserLogout
        )

    def test_password_change_url(self):
        self.assertEqual(
            resolve(reverse('worktime:password_change')).func.view_class,
            PasswordChange
        )

    def test_time_off_status_url(self):
        self.assertEqual(
            resolve(reverse('worktime:time_off_status')).func.view_class,
            TimeOffStatusView
        )

    def test_time_off_request_url(self):
        self.assertEqual(
            resolve(reverse('worktime:time_off_request')).func.view_class,
            TimeOffRequestView
        )

    def test_time_off_list_url(self):
        self.assertEqual(
            resolve(reverse('worktime:time_off_list')).func.view_class,
            TimeOffListView
        )

    def test_time_off_accept_url(self):
        self.assertEqual(
            resolve(reverse('worktime:time_off_accept')).func,
            time_off_accept
        )

    def test_time_off_cancel_url(self):
        self.assertEqual(
            resolve(reverse('worktime:time_off_cancel')).func,
            time_off_cancel
        )

    def test_record_url(self):
        self.assertEqual(
            resolve(reverse('worktime:record')).func.view_class,
            TimeRecordView
        )

    def test_record_calendar_url(self):
        self.assertEqual(
            resolve(reverse('worktime:record_calendar')).func.view_class,
            TimeRecordCalendarView
        )

    def test_record_summary_url(self):
        self.assertEqual(
            resolve(reverse('worktime:record_summary')).func.view_class,
            TimeRecordSummaryView
        )

    def test_readme_url(self):
        self.assertEqual(
            resolve(reverse('worktime:readme')).func.view_class,
            ReadmeView
        )
