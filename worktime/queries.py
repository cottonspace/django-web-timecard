from django.db.models import Max, Min, OuterRef, Q, QuerySet, Subquery

from . import utils
from .models import BusinessCalendar, TimeRecord


def get_monthly_records(username: str, year: int, month: int) -> QuerySet:
    """指定したユーザと年月の打刻情報を取得します。

    Args:
        username (str): ユーザ ID
        year (int): 西暦年
        month (int): 月

    Returns:
        QuerySet: 取得したクエリ結果
    """
    subquery = TimeRecord.objects.filter(date=OuterRef('date')).values('date').annotate(
        begin_record=Min('time', filter=Q(action='出勤', username=username)),
        end_record=Max('time', filter=Q(action='退勤', username=username))
    )
    queryset = BusinessCalendar.objects.filter(date__year=year, date__month=month).annotate(
        begin_record=Subquery(subquery.values('begin_record')),
        end_record=Subquery(subquery.values('end_record'))
    ).values(
        'date',
        'holiday',
        'attendance',
        'begin',
        'end',
        'leave',
        'back',
        'begin_record',
        'end_record'
    )
    for record in queryset:
        record.update(utils.worktime_calculation(record))
    return queryset
