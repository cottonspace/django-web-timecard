from django.conf import settings


def app_context(request) -> dict:
    """アプリケーション全体で使用するコンテキストを返却します。

    Args:
        request: 要求データ

    Returns:
        dict: コンテキストを格納した dict
    """
    return {
        'APP_SITE': settings.APP_SITE,
        'APP_NAME': settings.APP_NAME,
        'APP_VERSION': settings.APP_VERSION,
    }
