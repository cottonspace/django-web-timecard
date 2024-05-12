from django.test import TestCase

from worktime.rules import *


class TestWorktimeCalculationRulesValidations(TestCase):
    def get_attendance(self, days):
        yesterday = datetime.datetime.now().date() + datetime.timedelta(days=days)
        return {
            'date': yesterday,
            'holiday': None,
            'attendance': True,
            'begin': datetime.time(9, 0, 0),
            'end': datetime.time(17, 0, 0),
            'leave': datetime.time(12, 0, 0),
            'back': datetime.time(13, 0, 0),
            'begin_record': None,
            'end_record': None,
        }

    def test_record_not_found(self):
        obj = self.get_attendance(-1)
        self.assertEqual(worktime_calculation(obj)['error'], '打刻がありません')

    def test_begin_not_found(self):
        obj = self.get_attendance(-1)
        obj['end_record'] = datetime.time(18, 0, 0),
        self.assertEqual(worktime_calculation(obj)['error'], '出勤がありません')

    def test_end_not_found(self):
        obj = self.get_attendance(-1)
        obj['begin_record'] = datetime.time(8, 0, 0),
        self.assertEqual(worktime_calculation(obj)['error'], '退勤がありません')

    def test_time_invert(self):
        obj = self.get_attendance(-1)
        obj['begin_record'] = datetime.time(18, 0, 0),
        obj['end_record'] = datetime.time(8, 0, 0),
        self.assertEqual(worktime_calculation(obj)['error'], '出勤と退勤の順序が不正です')

    def test_future_record(self):
        obj = self.get_attendance(1)
        obj['begin_record'] = datetime.time(8, 0, 0),
        obj['end_record'] = datetime.time(18, 0, 0),
        self.assertEqual(worktime_calculation(obj)['error'], '未来日の打刻です')

    def test_future_not_record_yet(self):
        obj = self.get_attendance(1)
        self.assertEqual(worktime_calculation(obj), {
                         'past': False, 'work': False, 'behind': 0, 'early': 0, 'overtime': 0, 'error': None})


class TestWorktimeCalculationRulesCalculations(TestCase):
    def get_attendance(self, break_time=True):
        yesterday = datetime.datetime.now().date() - datetime.timedelta(days=1)
        obj = {
            'date': yesterday,
            'holiday': None,
            'attendance': True,
            'begin': datetime.time(9, 0, 0),
            'end': datetime.time(17, 0, 0),
            'leave': None,
            'back': None,
            'begin_record': None,
            'end_record': None,
        }
        if break_time:
            obj['leave'] = datetime.time(12, 0, 0)
            obj['back'] = datetime.time(13, 0, 0)
        return obj

    def test_no_gap(self):
        obj = self.get_attendance()
        obj['begin_record'] = datetime.time(9, 0, 0)
        obj['end_record'] = datetime.time(17, 0, 0)
        self.assertEqual(worktime_calculation(obj), {
                         'past': True, 'work': True, 'behind': 0, 'early': 0, 'overtime': 0, 'error': None})

    def test_arriving_late(self):
        obj = self.get_attendance()
        obj['begin_record'] = datetime.time(10, 0, 0)
        obj['end_record'] = datetime.time(17, 0, 0)
        self.assertEqual(worktime_calculation(obj), {
                         'past': True, 'work': True, 'behind': 60, 'early': 0, 'overtime': 0, 'error': None})

    def test_leaving_early(self):
        obj = self.get_attendance()
        obj['begin_record'] = datetime.time(9, 0, 0)
        obj['end_record'] = datetime.time(16, 0, 0)
        self.assertEqual(worktime_calculation(obj), {
                         'past': True, 'work': True, 'behind': 60, 'early': 0, 'overtime': 0, 'error': None})

    def test_early_begin(self):
        obj = self.get_attendance()
        obj['begin_record'] = datetime.time(8, 0, 0)
        obj['end_record'] = datetime.time(17, 0, 0)
        self.assertEqual(worktime_calculation(obj), {
                         'past': True, 'work': True, 'behind': 0, 'early': 60, 'overtime': 0, 'error': None})

    def test_later_end(self):
        obj = self.get_attendance()
        obj['begin_record'] = datetime.time(9, 0, 0)
        obj['end_record'] = datetime.time(18, 0, 0)
        self.assertEqual(worktime_calculation(obj), {
                         'past': True, 'work': True, 'behind': 0, 'early': 0, 'overtime': 60, 'error': None})

    def test_arriving_late_in_break_time(self):
        obj1 = self.get_attendance()
        obj1['begin_record'] = datetime.time(12, 0, 0)
        obj1['end_record'] = datetime.time(17, 0, 0)
        obj2 = self.get_attendance()
        obj2['begin_record'] = datetime.time(13, 0, 0)
        obj2['end_record'] = datetime.time(17, 0, 0)
        self.assertEqual(worktime_calculation(
            obj1), worktime_calculation(obj2))

    def test_leaving_early_in_break_time(self):
        obj1 = self.get_attendance()
        obj1['begin_record'] = datetime.time(9, 0, 0)
        obj1['end_record'] = datetime.time(12, 0, 0)
        obj2 = self.get_attendance()
        obj2['begin_record'] = datetime.time(9, 0, 0)
        obj2['end_record'] = datetime.time(13, 0, 0)
        self.assertEqual(worktime_calculation(
            obj1), worktime_calculation(obj2))

    def test_arriving_late_in_break_time_at_no_breaktime_day(self):
        obj1 = self.get_attendance(False)
        obj2 = self.get_attendance(False)
        obj1['begin_record'] = datetime.time(12, 0, 0)
        obj1['end_record'] = datetime.time(17, 0, 0)
        obj2['begin_record'] = datetime.time(13, 0, 0)
        obj2['end_record'] = datetime.time(17, 0, 0)
        result1 = worktime_calculation(obj1)
        result2 = worktime_calculation(obj2)
        self.assertEqual(result2['behind']-result1['behind'], 60)

    def test_leaving_early_in_break_time_at_no_breaktime_day(self):
        obj1 = self.get_attendance(False)
        obj2 = self.get_attendance(False)
        obj1['begin_record'] = datetime.time(9, 0, 0)
        obj1['end_record'] = datetime.time(12, 0, 0)
        obj2['begin_record'] = datetime.time(9, 0, 0)
        obj2['end_record'] = datetime.time(13, 0, 0)
        result1 = worktime_calculation(obj1)
        result2 = worktime_calculation(obj2)
        self.assertEqual(result1['behind']-result2['behind'], 60)
