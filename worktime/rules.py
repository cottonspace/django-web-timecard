"""
勤務時間計算の規則を定義するモジュールです。
"""
import datetime
from decimal import ROUND_CEILING, ROUND_FLOOR

from worktime.utils import delta, minutes_to_hours


def worktime_calculation(obj) -> dict:
    """勤務時間ルールと打刻時間から勤務実績を計算します。

    Args:
        obj: 打刻記録オブジェクト

    Raises:
        ValueError: 打刻エラー

    Returns:
        dict: 計算結果の dict
    """

    # 初期化
    result = {
        'work': obj['begin_record'] is not None or obj['end_record'] is not None,
        'behind':  0,
        'early': 0,
        'overtime': 0,
        'error': None
    }

    # 本日の日付
    today = datetime.datetime.now().date()

    # データチェック
    try:
        # 過去日の場合
        if obj['date'] < today:
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
        elif obj['date'] == today:
            if obj['begin_record'] is None or obj['end_record'] is None:
                # 本日で打刻なしまたは不完全打刻 (正常)
                return result
            else:
                # 本日で出退勤打刻の両方あるが前後矛盾
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
        result['overtime'] = delta(obj['begin_record'], obj['end_record'])
        return result

    # 標準勤務時間と実働時間の算出
    if obj['leave'] is not None and obj['back'] is not None:
        section1_total = delta(obj['begin'], obj['leave'])
        section1_record = max(0, delta(
            max(obj['begin'], obj['begin_record']),
            min(obj['end_record'], obj['leave'])
        ))
        section2_total = delta(obj['back'], obj['end'])
        section2_record = max(0, delta(
            max(obj['back'], obj['begin_record']),
            min(obj['end_record'], obj['end'])
        ))
    else:
        section1_total = delta(obj['begin'], obj['end'])
        section1_record = max(0, delta(
            max(obj['begin'], obj['begin_record']),
            min(obj['end_record'], obj['end'])
        ))
        section2_total = 0
        section2_record = 0

    # 不足時間の算出
    result['behind'] = (section1_total - section1_record) + \
        (section2_total - section2_record)

    # 早出時間の算出
    result['early'] = max(0, delta(
        obj['begin_record'],
        min(obj['end_record'], obj['begin'])
    ))

    # 残業時間の算出
    result['overtime'] = max(0, delta(
        max(obj['end'], obj['begin_record']),
        obj['end_record']
    ))

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
        'work_days': 0,
        'behind_minutes': 0,
        'behind_count': 0,
        'early_minutes': 0,
        'early_count': 0,
        'overtime_minutes': 0,
        'overtime_count': 0,
        'time_off_count': 0,
        'time_off_not_yet_accepted_count': 0,
        'errors': 0
    }

    # 全オブジェクトを加算
    for obj in objects:
        result['days'] += 1
        if obj['attendance']:
            result['attendance_days'] += 1
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
        if obj.get('time_off_request_id'):
            result['time_off_count'] += 1
            if not obj['time_off_accepted']:
                result['time_off_not_yet_accepted_count'] += 1

    # 時間単位の算出
    result['behind_hours'] = minutes_to_hours(
        result['behind_minutes'],
        '0.1',
        ROUND_FLOOR
    )
    result['early_hours'] = minutes_to_hours(
        result['early_minutes'],
        '0.1',
        ROUND_CEILING
    )
    result['overtime_hours'] = minutes_to_hours(
        result['overtime_minutes'],
        '0.1',
        ROUND_CEILING
    )

    # 結果返却
    return result
