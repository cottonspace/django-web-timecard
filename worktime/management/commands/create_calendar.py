import calendar
import datetime

import requests
from django.core.management.base import BaseCommand

import timecard.settings
from worktime.models import BusinessCalendar, StandardWorkPattern


def download_json(url: str):
    """インターネットから JSON データを取得します。

    Args:
        url (str): URL

    Raises:
        Exception: ダウンロード失敗

    Returns:
        Any: ダウンロードした JSON データ
    """
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        return json_data
    else:
        raise Exception("Failed to download from {0}.".format(url))


class Command(BaseCommand):
    """営業日カレンダを生成します。

    Args:
        BaseCommand: 基底コマンド
    """
    help = 'Create monthly calendar.'

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

            # 完了メッセージ
            self.stdout.write(self.style.SUCCESS(
                'Calendar %s created.' % (date.strftime("%Y-%m-%d"),)))

    def handle(self, *args, **options):
        """カスタムコマンドの処理を実行します。
        """

        # 祝日データをダウンロード
        holidays = download_json(timecard.settings.HOLIDAY_DOWNLOAD_URL)
        holidays_dates = list(holidays.keys())
        holidays_dates.sort(reverse=True)
        max_holiday = datetime.datetime.strptime(holidays_dates[0], "%Y-%m-%d")
        self.stdout.write(self.style.SUCCESS(max_holiday.strftime(
            'Holiday data up to %Y-%m has been downloaded.')))

        # 作成対象期間の最終日を算出
        now = datetime.datetime.now()
        current_months = now.year * 12 + (now.month - 1)
        months_1 = max_holiday.year * 12 + (max_holiday.month - 1)
        months_2 = current_months + timecard.settings.CALENDAR_MONTHS
        earlier_months = min(months_1, months_2)

        # 対象の月をループ処理
        months = current_months
        while months <= earlier_months:

            # 対象の年月を算出
            year = months // 12
            month = (months % 12) + 1

            # 対象月のデータが未作成の場合は作成
            first_date_of_month = datetime.datetime(year, month, 1)
            if not BusinessCalendar.objects.filter(date=first_date_of_month).exists():
                self.create_calendar(holidays, year, month)

            # 次の月を処理
            months += 1

        # 完了メッセージ
        self.stdout.write(self.style.SUCCESS('Calendar updated successfully.'))
