import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.db.models import Max, Min, OuterRef, Q, QuerySet, Subquery
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView

import timecard.settings

from . import utils
from .forms import (CustomAuthenticationForm, CustomPasswordChangeForm,
                    TimeRecordCalendarForm, TimeRecordForm)
from .models import BusinessCalendar, TimeRecord


class UserLogin(LoginView):
    """ログイン画面のビュー
    """
    form_class = CustomAuthenticationForm
    template_name = 'worktime/auth_login.html'
    redirect_field_name = 'redirect'
    redirect_authenticated_user = True


class UserLogout(LogoutView):
    """ログアウト画面のビュー
    """
    pass


class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    """パスワード変更画面のビュー
    """
    form_class = CustomPasswordChangeForm
    template_name = 'worktime/password_change.html'
    success_url = reverse_lazy('worktime:record')

    def form_valid(self, form):
        """フォームの検査
        """
        messages.success(self.request, 'パスワードが更新されました')
        return super().form_valid(form)


class TimeRecordView(LoginRequiredMixin, FormView):
    """打刻画面のビュー
    """
    template_name = 'worktime/record.html'
    form_class = TimeRecordForm
    success_url = reverse_lazy('worktime:record')

    def get_context_data(self, *args, **kwargs):
        """コンテキストの返却
        """
        date_from = datetime.datetime.now().date() - datetime.timedelta(days=2)
        context = super().get_context_data(*args, **kwargs)
        context["is_enable_check_location"] = timecard.settings.ENABLE_CHECK_LOCATION
        context["display_name"] = utils.display_name(self.request.user)
        context["recent"] = TimeRecord.objects.filter(username=self.request.user.username).filter(
            date__gte=date_from).order_by("-date", "-time")
        return context

    def string_to_float(self, string: str) -> float:
        """文字列を数値で取得します。

        Args:
            string (str): 文字列

        Returns:
            float: 数値
        """
        return float(string) if string else None

    def form_valid(self, form):
        """フォームの検査
        """
        now = datetime.datetime.now()
        action = form.cleaned_data['action']
        TimeRecord.objects.create(
            date=now.date(),
            time=now.time(),
            username=self.request.user.username,
            action=action,
            latitude=self.string_to_float(form.cleaned_data['latitude']),
            longitude=self.string_to_float(form.cleaned_data['longitude']),
            accuracy=self.string_to_float(form.cleaned_data['accuracy']),
            ua=form.cleaned_data['ua'],
        )
        if action == '出勤':
            sound = 'sound_begin'
        elif action == '退勤':
            sound = 'sound_end'
        else:
            sound = None
        messages.success(self.request, action + 'の打刻が完了しました', sound)
        return super().form_valid(form)


class TimeRecordCalendarView(LoginRequiredMixin, FormView):
    """勤務表画面のビュー
    """
    template_name = 'worktime/record_calendar.html'
    form_class = TimeRecordCalendarForm

    def query_records(self, username: str, year: int, month: int) -> QuerySet:
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

    def get_context_data(self, **kwargs):
        """コンテキストの返却
        """
        context = super().get_context_data(**kwargs)
        if self.request.user.is_staff:
            context['username'] = self.request.GET.get(
                'username', self.request.user.username)
        else:
            context['username'] = self.request.user.username
        today = datetime.datetime.today()
        context['year'] = int(self.request.GET.get('year', today.year))
        context['month'] = int(self.request.GET.get('month', today.month))
        context['entries'] = self.query_records(
            context['username'], context['year'], context['month'])
        context['summary'] = utils.summarize(context['entries'])
        context['users'] = utils.get_users(False)
        return context

    def get_initial(self):
        """初期値の取得
        """
        initial = super().get_initial()
        initial['username'] = self.request.GET.get(
            'username', self.request.user.username)
        return initial

    def form_valid(self, form):
        """フォームの検査
        """
        username = form.cleaned_data['username']
        year = form.cleaned_data['year']
        month = form.cleaned_data['month']
        return redirect(reverse('worktime:record_calendar') + f'?username={username}&year={year}&month={month}')


class ReadmeView(TemplateView):
    """説明画面のビュー
    """
    template_name = 'worktime/readme.html'

    def get_context_data(self, *args, **kwargs):
        """コンテキストの返却
        """
        context = super().get_context_data(*args, **kwargs)
        context["MAX_DISTANCE"] = timecard.settings.MAX_DISTANCE
        context["MIN_BEHIND_MIN"] = timecard.settings.MIN_BEHIND_MIN
        context["MIN_EARLY_MIN"] = timecard.settings.MIN_EARLY_MIN
        context["MIN_OVERTIME_MIN"] = timecard.settings.MIN_OVERTIME_MIN
        context["ENABLE_CHECK_LOCATION"] = timecard.settings.ENABLE_CHECK_LOCATION
        return context
