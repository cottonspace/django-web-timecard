"""
URL ディスパッチャです。
"""
from django.urls import path

from worktime.views import (PasswordChange, ReadmeView, TimeOffListView,
                            TimeOffRequestView, TimeOffStatusView,
                            TimeRecordCalendarView, TimeRecordSummaryView,
                            TimeRecordView, UserLogin, UserLogout,
                            api_record_summary, api_users_list,
                            time_off_accept, time_off_cancel)

# アプリケーション名
app_name = "worktime"

# URL パターン
urlpatterns = [
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('password_change/', PasswordChange.as_view(), name='password_change'),
    path('time_off/status/', TimeOffStatusView.as_view(), name='time_off_status'),
    path('time_off/request/', TimeOffRequestView.as_view(), name='time_off_request'),
    path('time_off/list/', TimeOffListView.as_view(), name='time_off_list'),
    path('time_off/accept/', time_off_accept, name='time_off_accept'),
    path('time_off/cancel/', time_off_cancel, name='time_off_cancel'),
    path('record/', TimeRecordView.as_view(), name='record'),
    path('record/calendar/',
         TimeRecordCalendarView.as_view(),
         name='record_calendar'
         ),
    path('record/summary/', TimeRecordSummaryView.as_view(), name='record_summary'),
    path('readme/', ReadmeView.as_view(), name='readme'),
    path('api/users/list/', api_users_list, name='api_users_list'),
    path('api/record/summary/', api_record_summary, name='api_record_summary'),
]
