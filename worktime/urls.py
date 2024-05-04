from django.urls import path

from . import views

# アプリケーション名
app_name = "worktime"

# URL パターン
urlpatterns = [
    path('login/', views.UserLogin.as_view(), name='login'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('time_off/status/', views.TimeOffStatusView.as_view(),
         name='time_off_status'),
    path('time_off/request/', views.TimeOffRequestView.as_view(),
         name='time_off_request'),
    path('time_off/cancel', views.time_off_cancel, name='time_off_cancel'),
    path('record/', views.TimeRecordView.as_view(), name='record'),
    path('record/calendar/', views.TimeRecordCalendarView.as_view(),
         name='record_calendar'),
    path('record/summary/', views.TimeRecordSummaryView.as_view(),
         name='record_summary'),
    path('readme/', views.ReadmeView.as_view(), name='readme'),
]
