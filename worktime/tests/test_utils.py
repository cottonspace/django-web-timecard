from decimal import ROUND_CEILING, Decimal

from django.contrib.auth.models import User
from django.test import TestCase

from worktime.utils import *


class TestUserUtils(TestCase):
    def setUp(self):
        user1 = User.objects.create(
            username='active01', password='12345678', email='active01@example.com')
        user1.is_active = True
        user1.save()
        user2 = User.objects.create(
            username='inactive01', password='12345678', email='inactive01@example.com')
        user2.is_active = False
        user2.save()

    def test_display_name_first_last(self):
        user = User.objects.create(
            username='foo', password='bar', email='foo@example.com')
        user.first_name = 'foo'
        user.last_name = 'bar'
        self.assertEqual(display_name(user), 'bar foo')

    def test_display_name_first_only(self):
        user = User.objects.create(
            username='foo', password='bar', email='foo@example.com')
        user.first_name = 'foo'
        user.last_name = ''
        self.assertEqual(display_name(user), 'foo')

    def test_display_name_last_only(self):
        user = User.objects.create(
            username='foo', password='bar', email='foo@example.com')
        user.first_name = ''
        user.last_name = 'bar'
        self.assertEqual(display_name(user), 'bar')

    def test_get_users_active_only(self):
        self.assertEqual(get_users(True), {'active01': 'active01'})

    def test_get_users_all(self):
        self.assertEqual(get_users(False), {
                         'active01': 'active01', 'inactive01': 'inactive01 *'})


class TestDateTimeUtils(TestCase):
    def test_get_first_day_of_year_1(self):
        timecard.settings.YEAR_FIRST_MONTH = 1
        self.assertEqual(get_first_day_of_year(
            datetime.date(2024, 12, 31)), datetime.date(2024, 1, 1))
        self.assertEqual(get_first_day_of_year(
            datetime.date(2025, 1, 1)), datetime.date(2025, 1, 1))

    def test_get_first_day_of_year_4(self):
        timecard.settings.YEAR_FIRST_MONTH = 4
        self.assertEqual(get_first_day_of_year(
            datetime.date(2025, 3, 31)), datetime.date(2024, 4, 1))
        self.assertEqual(get_first_day_of_year(
            datetime.date(2025, 4, 1)), datetime.date(2025, 4, 1))

    def test_get_year_range_1(self):
        timecard.settings.YEAR_FIRST_MONTH = 1
        self.assertEqual(get_year_range(2024), (datetime.date(
            2024, 1, 1), datetime.date(2025, 1, 1)))

    def test_get_year_range_4(self):
        timecard.settings.YEAR_FIRST_MONTH = 4
        self.assertEqual(get_year_range(2024), (datetime.date(
            2024, 4, 1), datetime.date(2025, 4, 1)))

    def test_delta(self):
        self.assertEqual(delta(datetime.time(0, 0, 0),
                         datetime.time(0, 0, 1)), 0)
        self.assertEqual(delta(datetime.time(0, 0, 0),
                         datetime.time(0, 1, 0)), 1)
        self.assertEqual(delta(datetime.time(0, 0, 0),
                         datetime.time(1, 0, 0)), 60)
        self.assertEqual(delta(datetime.time(0, 0, 0),
                         datetime.time(23, 59, 59)), 23*60+59)

    def test_minutes_to_hours(self):
        self.assertEqual(minutes_to_hours(
            0, '0.1', ROUND_CEILING), Decimal('0.0'))
        self.assertEqual(minutes_to_hours(
            30, '0.1', ROUND_CEILING), Decimal('0.5'))
        self.assertEqual(minutes_to_hours(
            60, '0.1', ROUND_CEILING), Decimal('1.0'))
