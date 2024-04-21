from django.urls import path

from . import views

# アプリケーション名
app_name = "worktime"

# URL パターン
urlpatterns = [
    path('login/', views.UserLogin.as_view(), name='login'),
    path('logout/', views.UserLogout.as_view(), name='logout'),
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('record/', views.TimeRecordView.as_view(), name='record'),
    path('record/calendar/', views.TimeRecordCalendarView.as_view(),
         name='record_calendar'),
    path('readme/', views.ReadmeView.as_view(), name='readme'),
]
