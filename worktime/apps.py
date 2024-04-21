from django.apps import AppConfig


class WorktimeConfig(AppConfig):
    """アプリケーション定義

    Args:
        AppConfig: 継承するクラス
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'worktime'
    verbose_name = 'Web タイムカード'
