"""
ユーティリティメソッドです。
"""
import datetime
from decimal import Decimal

from django.contrib.auth.models import User

import timecard.settings


def display_name(user) -> str:
    """ユーザ名を表示形式に編集します。

    Args:
        user (obj): ユーザオブジェクト

    Returns:
        str: 表示文字列
    """
    if user is None:
        return None
    if user.last_name or user.first_name:
        return (user.last_name + ' ' + user.first_name).strip()
    return user.username


def get_users(active: bool) -> dict:
    """存在するユーザの ID と表示形式の文字列の dict を取得します。

    Args:
        active (bool): 有効なユーザのみ取得する場合は True

    Returns:
        dict: ユーザ ID と表示形式の文字列の dict
    """
    if active:
        users = User.objects.filter(is_superuser=False, is_active=True)
    else:
        users = User.objects.filter(is_superuser=False)
    results = {}
    for user in users.order_by('-is_active', 'last_name', 'first_name', 'username'):
        if user.is_active:
            results[user.username] = display_name(user)
        else:
            results[user.username] = display_name(user) + ' *'
    return results


def truncate_text(text: str, length: int, ellipsis: str) -> str:
    """指定した長さより長い文字列を省略します。

    Args:
        text (str): 元の文字列
        length (int): 制限する長さ
        ellipsis (str): 省略記号

    Returns:
        str: 処理結果の文字列
    """
    if text is None:
        return None
    return text[:length] + (ellipsis if text[length:] else '')


def get_first_day_of_year(day: datetime.date) -> datetime.date:
    """指定した日を含む年度の最初の日を取得します。

    Args:
        day (datetime.date): 日

    Returns:
        datetime.date: 指定した日を含む年度の最初の日
    """
    first_month = timecard.settings.YEAR_FIRST_MONTH
    if first_month <= day.month:
        return datetime.date(day.year, first_month, 1)
    else:
        return datetime.date(day.year - 1, first_month, 1)


def get_year_range(year: int) -> tuple[datetime.date, datetime.date]:
    """指定した年度の期間を取得します。

    Args:
        year (int): 年度

    Returns:
        tuple[datetime.date,datetime.date]: 指定した年度の最初の日と翌年度の最初の日
    """
    first_month = timecard.settings.YEAR_FIRST_MONTH
    return datetime.date(year, first_month, 1), datetime.date(year + 1, first_month, 1)


def delta(time1: datetime.time, time2: datetime.time) -> int:
    """時刻の差を分で取得します。

    Args:
        time1 (datetime.time): 1個目の時刻
        time2 (datetime.time): 2個目の時刻

    Returns:
        int: 1個目の時刻から2個目の時刻までの分数
    """
    seconds1 = time1.hour * 60 + time1.minute
    seconds2 = time2.hour * 60 + time2.minute
    return seconds2 - seconds1


def minutes_to_hours(minutes: int, quantize: str, rounding_mode) -> Decimal:
    """整数の分から時間の単位に変換します。

    Args:
        minutes (int): 分
        quantize (str): 精度
        rounding_mode: 丸めモード

    Returns:
        Decimal: 時間単位の値
    """
    return (Decimal(minutes) / Decimal(60)).quantize(Decimal(quantize), rounding=rounding_mode)
