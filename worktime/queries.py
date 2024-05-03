from django.db.models import Max, Min, OuterRef, Q, QuerySet, Subquery

from . import utils
from .models import BusinessCalendar, TimeOffRequest, TimeRecord


def get_monthly_records(username: str, year: int, month: int) -> QuerySet:
    """指定したユーザと年月の打刻情報を取得します。

    Args:
        username (str): ユーザ ID
        year (int): 西暦年
        month (int): 月

    Returns:
        QuerySet: 取得したクエリ結果
    """
    subquery = TimeRecord.objects.filter(date=OuterRef('date'), username=username).values('date').annotate(
        begin_record=Min('time', filter=Q(action='出勤')),
        end_record=Max('time', filter=Q(action='退勤'))
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
    queryset_time_off_requests = TimeOffRequest.objects.filter(date__year=year, date__month=month, username=username).values(
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
    for record in queryset_records:
        time_off_requests = queryset_time_off_requests.filter(
            date=record['date'])
        if time_off_requests.exists():
            time_off_request = time_off_requests[0]
            if time_off_request['accepted']:
                record.update({
                    'time_off_request_id': time_off_request['id'],
                    'holiday': time_off_request['display_name'],
                    'attendance': time_off_request['attendance'],
                    'begin': time_off_request['begin'],
                    'end': time_off_request['end'],
                    'leave': time_off_request['leave'],
                    'back': time_off_request['back']
                })
            else:
                record.update({
                    'time_off_request_id': time_off_request['id'],
                    'holiday': time_off_request['display_name']+' (承認待ち)'
                })
        record.update(utils.worktime_calculation(record))
    return queryset_records
