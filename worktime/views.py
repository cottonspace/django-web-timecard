import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView

import timecard.settings

from . import queries, utils
from .forms import (CustomAuthenticationForm, CustomPasswordChangeForm,
                    TimeRecordCalendarForm, TimeRecordForm)
from .models import TimeRecord


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
        context['entries'] = queries.get_monthly_records(
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
