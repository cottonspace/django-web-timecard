"""
営業日カレンダ削除 の CLI 管理コマンドです。
"""
import datetime

from django.core.management.base import BaseCommand

from worktime.models import BusinessCalendar


class Command(BaseCommand):
    """指定した年月とそれ以降の営業日カレンダを削除します。

    Args:
        BaseCommand: 基底コマンド
    """
    help = 'Delete calendars for the specified month and beyond months.'

    def add_arguments(self, parser):
        """実行時引数を設定します。

        Args:
            parser: コマンドライン解析クラス
        """
        parser.add_argument('year', type=int)
        parser.add_argument('month', type=int)

    def handle(self, *args, **options):
        """カスタムコマンドの処理を実行します。
        """

        # 引数を取得
        year = options['year']
        month = options['month']

        # 削除開始日を設定
        delete_from = datetime.datetime(year, month, 1)

        # 対象レコードを削除
        BusinessCalendar.objects.filter(date__gte=delete_from).delete()

        # 完了メッセージ
        self.stdout.write(self.style.SUCCESS('Calendar deleted.'))
