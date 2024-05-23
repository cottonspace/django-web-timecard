"""
データベース問い合わせのモジュールです。
"""
import datetime

from django.db.models import Count, Max, Min, OuterRef, Q, Subquery

from worktime.models import BusinessCalendar, TimeOffRequest, TimeRecord
from worktime.rules import worktime_calculation


def count_time_off_requests(username: str, date_range: tuple[datetime.date, datetime.date]) -> dict:
    """指定したユーザが指定期間に申請した休暇申請の数を取得します。

    Args:
        username (str): ユーザ ID
        date_range (tuple[datetime.date, datetime.date]): 期間 (終了日は範囲に含まれません)

    Returns:
        dict: 休暇名称をキーにした申請回数の dict
    """
    results = {}
    begin, end = date_range
    for record in TimeOffRequest.objects.filter(date__gte=begin, date__lt=end, username=username).values('display_name').annotate(count=Count('id')):
        results[record['display_name']] = record['count']
    return results


def get_monthly_time_off_requests(username: str, year: int, month: int) -> dict:
    """指定したユーザと年月の休暇申請を取得します。

    Args:
        username (str): ユーザ ID
        year (int): 西暦年
        month (int): 月

    Returns:
        dict: 日付をキーにした休暇申請情報の dict
    """
    records = TimeOffRequest.objects.filter(date__year=year, date__month=month, username=username).values(
        'id',
        'date',
        'display_name',
        'attendance',
        'begin',
        'end',
        'leave',
        'back',
        'accepted'
    )
    results = {}
    for record in records:
        results[record['date']] = record
    return results


def get_monthly_records(username: str, year: int, month: int) -> list:
    """指定したユーザと年月の打刻記録を取得します。承認済の休暇申請は勤務時間の計算に反映されます。

    Args:
        username (str): ユーザ ID
        year (int): 西暦年
        month (int): 月

    Returns:
        list: 打刻記録のリスト(日付順)
    """
    subquery = TimeRecord.objects.filter(date=OuterRef('date'), username=username).values('date').annotate(
        begin_record=Min('time', filter=Q(action='begin')),
        end_record=Max('time', filter=Q(action='end'))
    )
    queryset_records = BusinessCalendar.objects.filter(date__year=year, date__month=month).order_by('date').annotate(
        begin_record=Subquery(subquery.values('begin_record')),
        end_record=Subquery(subquery.values('end_record')),
    ).values(
        'date',
        'holiday',
        'attendance',
        'begin',
        'end',
        'leave',
        'back',
        'begin_record',
        'end_record',
    )
    records = list(queryset_records.values())
    time_off_requests = get_monthly_time_off_requests(username, year, month)
    for record in records:
        time_off_request = time_off_requests.get(record['date'])
        if time_off_request:
            time_off_accepted = time_off_request['accepted']
            record.update({
                'time_off_request_id': time_off_request['id'],
                'time_off_accepted': time_off_accepted,
                'holiday': '休暇 (' + time_off_request['display_name'] + ')' + ('' if time_off_accepted else ' (承認待ち)')
            })
            if time_off_accepted:
                record.update({
                    'attendance': time_off_request['attendance'],
                    'begin': time_off_request['begin'],
                    'end': time_off_request['end'],
                    'leave': time_off_request['leave'],
                    'back': time_off_request['back']
                })
        record.update(worktime_calculation(record))
    return records
