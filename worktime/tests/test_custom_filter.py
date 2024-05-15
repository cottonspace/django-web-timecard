from decimal import Decimal

from django.test import TestCase

from worktime.templatetags.custom_filter import (dict_value, dump_default,
                                                 json_dumps)


class TestCustomFilters(TestCase):
    def test_customfilter_dict_value_exists(self):
        dict = {'foo': 'bar'}
        self.assertEqual(dict_value(dict, 'foo'), 'bar')

    def test_customfilter_dict_value_not_exists(self):
        dict = {'foo': 'bar'}
        self.assertEqual(dict_value(dict, 'baz'), None)

    def test_customfilter_dump_default_str(self):
        with self.assertRaises(TypeError):
            dump_default('foo')

    def test_customfilter_dump_default_decimal(self):
        self.assertEqual(dump_default(Decimal('1.0')), 1)

    def test_customfilter_json_dumps(self):
        dict = {'foo': 'bar'}
        self.assertEqual(json_dumps(dict), '{"foo": "bar"}')
