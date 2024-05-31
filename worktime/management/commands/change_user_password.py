"""
ユーザのパスワードを非対話型で更新する CLI 管理コマンドです。
"""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """ユーザのパスワードを非対話型で更新します。

    Args:
        BaseCommand: 基底コマンド
    """
    help = 'Change user password non-interactively.'

    def add_arguments(self, parser):
        """実行時引数を設定します。

        Args:
            parser: コマンドライン解析クラス
        """
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)

    def handle(self, *args, **options):
        """カスタムコマンドの処理を実行します。
        """

        # パスワードを設定
        username = options['username']
        password = options['password']
        try:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()

            # 完了メッセージ
            self.stdout.write(self.style.SUCCESS(
                'Password changed successfully.'))

        except Exception:

            # エラーメッセージ
            self.stdout.write(self.style.ERROR('Password change failed.'))
