import calendar
import datetime

import pytz
import requests
from django.core.management.base import BaseCommand
from django.db.models import Max
from ics import Calendar

import timecard.settings
from worktime.models import BusinessCalendar, StandardWorkPattern


class Command(BaseCommand):
    """営業日カレンダを生成します。

    Args:
        BaseCommand: 基底コマンド
    """
    help = 'Create monthly calendar.'

    def download_ics(self, url: str, zone: str) -> dict:
        """ics 形式のイベントデータをダウンロードします。

        Args:
            url (str): URL
            tz (str): タイムゾーン

        Returns:
            dict: ダウンロードしたイベントデータ
        """
        cal = Calendar(requests.get(url).text)
        service_zone = pytz.timezone(zone)
        events = {}
        for event in cal.events:
            if event.begin.datetime:
                events[event.begin.astimezone(
                    service_zone).strftime('%Y-%m-%d')] = event.name
        return dict(sorted(events.items()))

    def get_months(self, date) -> int:
        """日付の月数を計算します。

        Args:
            date: 日時または日付

        Returns:
            int: 月数
        """
        return date.year * 12 + date.month - 1

    def create_calendar(self, holidays: dict, year: int, month: int):
        """指定した年月のカレンダを生成します。

        Args:
            holidays (dict): 祝日の日付と名称の dict
            year (int): 西暦年
            month (int): 月
        """

        # 月内のすべての日をループ
        for day in range(1, calendar.monthrange(year, month)[1] + 1):

            # 対象日付
            date = datetime.datetime(year, month, day)

            # 祝日に該当するか判定
            holiday = ''
            str_date = date.strftime('%Y-%m-%d')
            national_holiday = holidays.get(str_date, '')
            if national_holiday:
                holiday = '休日 (' + national_holiday + ')'
                pattern = StandardWorkPattern.objects.get(pk=7)
            else:
                pattern = StandardWorkPattern.objects.get(pk=date.weekday())
                if not pattern.attendance:
                    holiday = '定休日'

            # 営業日レコードを生成
            BusinessCalendar.objects.create(date=date,
                                            holiday=holiday,
                                            attendance=pattern.attendance,
                                            begin=pattern.begin,
                                            end=pattern.end,
                                            leave=pattern.leave,
                                            back=pattern.back
                                            )
            self.stdout.write(self.style.SUCCESS(
                date.strftime('%Y-%m-%d created.')))

    def handle(self, *args, **options):
        """カスタムコマンドの処理を実行します。
        """

        # 祝日データ (ics) をダウンロード
        if timecard.settings.HOLIDAY_DOWNLOAD_URL:
            holidays = self.download_ics(
                timecard.settings.HOLIDAY_DOWNLOAD_URL, timecard.settings.TIME_ZONE)
            holidays_dates = list(holidays.keys())
            holidays_dates.sort(reverse=True)
            max_holiday = datetime.datetime.strptime(
                holidays_dates[0], "%Y-%m-%d")
            self.stdout.write(self.style.SUCCESS(
                max_holiday.strftime('Holiday data downloaded up to %Y-%m.')))
        else:
            holidays = {}
            max_holiday = datetime.datetime.max

        # 現在の日付を取得
        now = datetime.datetime.now()

        # 作成対象の先頭月を算出
        max_created_date = BusinessCalendar.objects.aggregate(max_date=Max('date'))[
            'max_date']
        if max_created_date is None:
            start_months = self.get_months(now)
        else:
            start_months = self.get_months(max_created_date) + 1

        # 作成対象の最終月を算出
        months_1 = self.get_months(max_holiday)
        months_2 = self.get_months(now) + timecard.settings.CALENDAR_MONTHS
        end_months = min(months_1, months_2)

        # 対象の月をループ処理
        for months in range(start_months, end_months + 1):

            # 対象の年月を算出
            year = months // 12
            month = (months % 12) + 1

            # 対象月のデータを作成
            self.create_calendar(holidays, year, month)

        # 完了メッセージ
        self.stdout.write(self.style.SUCCESS('Calendar created.'))
