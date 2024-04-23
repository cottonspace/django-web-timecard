import timecard.settings


def app_context(request) -> dict:
    """アプリケーション全体で使用するコンテキストを返却します。

    Args:
        request: 要求データ

    Returns:
        dict: コンテキストを格納した dict
    """
    return {
        'APP_SITE': timecard.settings.APP_SITE,
        'APP_NAME': timecard.settings.APP_NAME,
        'APP_VERSION': timecard.settings.APP_VERSION,
    }
