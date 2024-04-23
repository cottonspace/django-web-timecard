import datetime
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal

from django.contrib.auth.models import User

import timecard.settings


def display_name(user) -> str:
    """ユーザ名を表示形式に編集します。

    Args:
        user (obj): ユーザオブジェクト

    Returns:
        str: 表示文字列
    """
    if user.last_name or user.first_name:
        display = (user.last_name + ' ' + user.first_name).strip()
    else:
        display = user.username
    return display


def get_users(active: bool) -> dict:
    """存在するユーザの ID と表示形式の文字列の dict を取得します。

    Args:
        active (bool): 有効なユーザのみ取得する場合は True

    Returns:
        dict: ユーザ ID と表示形式の文字列の dict
    """
    if active:
        users = User.objects.filter(is_active=True)
    else:
        users = User.objects
    results = {}
    for user in users.order_by('-is_active', 'last_name', 'first_name', 'username'):
        if user.is_active:
            results[user.username] = display_name(user)
        else:
            results[user.username] = display_name(user) + ' *'
    return results


def delta(time1: datetime.time, time2: datetime.time) -> int:
    """時刻の差を分で取得します。

    Args:
        time1 (datetime.time): 1個目の時刻
        time2 (datetime.time): 2個目の時刻

    Returns:
        int: 1個目の時刻から2個目の時刻までの分数
    """
    if time1 is not None and time2 is not None:
        seconds1 = time1.hour * 60 + time1.minute
        seconds2 = time2.hour * 60 + time2.minute
        return seconds2 - seconds1
    return 0


def cutout(threshold: int, value: int) -> int:
    """数値の切り捨てをおこないます。

    Args:
        threshold (int): 閾値
        value (int): 値

    Returns:
        int: 値が閾値未満の場合は 0 とみなした結果の値です。
    """
    if value < threshold:
        return 0
    return value


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


def worktime_calculation(obj) -> dict:
    """勤務時間ルールと打刻時間から勤務実績を計算します。

    Args:
        obj: 打刻情報オブジェクト

    Raises:
        ValueError: 打刻エラー

    Returns:
        dict: 計算結果の dict
    """

    # 初期化
    result = {
        'past': obj['date'] <= datetime.datetime.now().date(),
        'work': obj['begin_record'] is not None or obj['end_record'] is not None,
        'behind':  0,
        'early': 0,
        'overtime': 0,
        'error': None
    }

    # データチェック
    try:
        # 過去日の場合
        if result['past']:
            if obj['begin_record'] is None and obj['end_record'] is None:
                if obj['attendance']:
                    # 過去日で打刻なし
                    raise ValueError('打刻がありません')
                else:
                    # 非営業日で打刻なし (正常)
                    return result
            elif obj['begin_record'] is not None and obj['end_record'] is None:
                # 不完全打刻
                raise ValueError('退勤がありません')
            elif obj['begin_record'] is None and obj['end_record'] is not None:
                # 不完全打刻
                raise ValueError('出勤がありません')
            else:
                # 過去日で出退勤打刻の両方あるが前後矛盾
                if obj['end_record'] < obj['begin_record']:
                    raise ValueError('出勤と退勤の順序が不正です')
        else:
            if obj['begin_record'] is not None or obj['end_record'] is not None:
                # 未到来日で打刻あり
                raise ValueError('未来日の打刻です')
            else:
                # 未到来日で打刻なし (正常)
                return result
    except ValueError as e:
        result['error'] = e.args[0]
        return result

    # 非営業日の場合はすべて時間外として計算
    if not obj['attendance']:
        result['overtime'] = cutout(timecard.settings.MIN_OVERTIME_MIN, delta(
            obj['begin_record'], obj['end_record']))
        return result

    # 標準勤務時間と実働時間の算出
    if obj['leave'] is not None and obj['back'] is not None:
        section1_total = delta(obj['begin'], obj['leave'])
        section1_record = max(0, delta(
            max(obj['begin'], obj['begin_record']), min(obj['end_record'], obj['leave'])))
        section2_total = delta(obj['back'], obj['end'])
        section2_record = max(0, delta(
            max(obj['back'], obj['begin_record']), min(obj['end_record'], obj['end'])))
    else:
        section1_total = delta(obj['begin'], obj['end'])
        section1_record = max(0, delta(
            max(obj['begin'], obj['begin_record']), min(obj['end_record'], obj['end'])))
        section2_total = 0
        section2_record = 0

    # 不足時間の算出
    result['behind'] = cutout(timecard.settings.MIN_BEHIND_MIN, (
        section1_total - section1_record) + (section2_total - section2_record))

    # 早出時間の算出
    result['early'] = cutout(timecard.settings.MIN_EARLY_MIN, max(
        0,  delta(obj['begin_record'], min(obj['end_record'], obj['begin']))))

    # 残業時間の算出
    result['overtime'] = cutout(timecard.settings.MIN_OVERTIME_MIN, max(
        0,  delta(max(obj['end'], obj['begin_record']), obj['end_record'])))

    # 結果返却
    return result


def summarize(objects) -> dict:
    """勤務実績のリストを集計します。

    Args:
        objects: 勤務実績のリスト

    Returns:
        dict: 集計結果の dict
    """
    # 初期化
    result = {
        'days': 0,
        'attendance_days': 0,
        'past_days': 0,
        'work_days': 0,
        'behind_minutes': 0,
        'behind_count': 0,
        'early_minutes': 0,
        'early_count': 0,
        'overtime_minutes': 0,
        'overtime_count': 0,
        'errors': 0
    }

    # 全オブジェクトを加算
    for obj in objects:
        result['days'] += 1
        if obj['attendance']:
            result['attendance_days'] += 1
        if obj['past']:
            result['past_days'] += 1
        if obj['work']:
            result['work_days'] += 1
        if obj['error']:
            result['errors'] += 1
        if 0 < obj['behind']:
            result['behind_minutes'] += obj['behind']
            result['behind_count'] += 1
        if 0 < obj['early']:
            result['early_minutes'] += obj['early']
            result['early_count'] += 1
        if 0 < obj['overtime']:
            result['overtime_minutes'] += obj['overtime']
            result['overtime_count'] += 1

    # 時間単位の算出
    result['behind_hours'] = minutes_to_hours(
        result['behind_minutes'], '0.1', ROUND_FLOOR)
    result['early_hours'] = minutes_to_hours(
        result['early_minutes'], '0.1', ROUND_CEILING)
    result['overtime_hours'] = minutes_to_hours(
        result['overtime_minutes'], '0.1', ROUND_CEILING)

    # 結果返却
    return result
