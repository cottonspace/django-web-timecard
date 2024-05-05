import datetime

from django.db.models import Count, Max, Min, OuterRef, Q, QuerySet, Subquery

from . import rules
from .models import BusinessCalendar, TimeOffRequest, TimeRecord


def count_time_off_requests(username: str, date_range: tuple[datetime.date, datetime.date]) -> dict:
    """指定したユーザが指定期間に申請した承認済の休暇申請の数を取得します。

    Args:
        username (str): ユーザ ID
        date_range (tuple[datetime.date, datetime.date]): 期間 (終了日は範囲に含まれません)

    Returns:
        dict: 休暇名称をキーにした取得回数の dict
    """
    results = {}
    begin, end = date_range
    for record in TimeOffRequest.objects.filter(date__gte=begin, date__lt=end, username=username, accepted=True).values('display_name').annotate(Count('display_name')):
        results[record['display_name']] = record['display_name__count']
    return results


def get_monthly_time_off_requests(username: str, year: int, month: int) -> QuerySet:
    """指定したユーザと年月の休暇申請を取得します。

    Args:
        username (str): ユーザ ID
        year (int): 西暦年
        month (int): 月

    Returns:
        QuerySet: 取得したクエリ結果
    """
    return TimeOffRequest.objects.filter(date__year=year, date__month=month, username=username).values(
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


def get_monthly_records(username: str, year: int, month: int) -> QuerySet:
    """指定したユーザと年月の打刻記録を取得します。承認済の休暇申請は勤務時間の計算に反映されます。

    Args:
        username (str): ユーザ ID
        year (int): 西暦年
        month (int): 月

    Returns:
        QuerySet: 取得したクエリ結果
    """
    subquery = TimeRecord.objects.filter(date=OuterRef('date'), username=username).values('date').annotate(
        begin_record=Min('time', filter=Q(action='begin')),
        end_record=Max('time', filter=Q(action='end'))
    )
    queryset_records = BusinessCalendar.objects.filter(date__year=year, date__month=month).annotate(
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
    queryset_time_off_requests = get_monthly_time_off_requests(
        username, year, month)
    for record in queryset_records:
        time_off_requests = queryset_time_off_requests.filter(
            date=record['date'])
        if time_off_requests.exists():
            time_off_request = time_off_requests[0]
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
        record.update(rules.worktime_calculation(record))
    return queryset_records
