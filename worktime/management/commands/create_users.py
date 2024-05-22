"""
ユーザ一括登録 の CLI 管理コマンドです。
"""
import csv

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ユーザを一括で登録します。

    Args:
        BaseCommand: 基底コマンド
    """
    help = 'Create all users in csv file.'

    def add_arguments(self, parser):
        """実行時引数を設定します。

        Args:
            parser: コマンドライン解析クラス
        """
        parser.add_argument('file', type=str)

    def handle(self, *args, **options):
        """カスタムコマンドの処理を実行します。
        """

        # ユーザレコードを生成
        f = open(options['file'], 'r', encoding='utf_8_sig')
        reader = csv.reader(f)
        for columns in reader:
            try:
                user = User(
                    username=columns[0],
                    last_name=columns[2],
                    first_name=columns[3]
                )
                user.set_password(columns[1])
                user.save()
                self.stdout.write(self.style.SUCCESS(columns[0] + ' ok'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    columns[0] + ' error (' + str(e) + ')'
                ))
        f.close()

        # 完了メッセージ
        self.stdout.write(self.style.SUCCESS('User created.'))
