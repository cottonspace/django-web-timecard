from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm


class CustomAuthenticationForm(AuthenticationForm):
    """ログイン画面のフォーム

    Args:
        AuthenticationForm: 継承するフォーム
    """

    def __init__(self, *args, **kwargs):
        """初期化
        """
        super().__init__(*args, **kwargs)

        # Bootstrap 対応
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class CustomPasswordChangeForm(PasswordChangeForm):
    """パスワード変更画面のフォーム

    Args:
        PasswordChangeForm: 継承するフォーム
    """

    def __init__(self, *args, **kwargs):
        """初期化
        """
        super().__init__(*args, **kwargs)

        # Bootstrap 対応
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class TimeRecordForm(forms.Form):
    """打刻画面のフォーム

    Args:
        forms: 継承するフォーム
    """
    action = forms.CharField(widget=forms.HiddenInput)
    latitude = forms.CharField(widget=forms.HiddenInput, required=False)
    longitude = forms.CharField(widget=forms.HiddenInput, required=False)
    accuracy = forms.CharField(widget=forms.HiddenInput, required=False)
    ua = forms.CharField(widget=forms.HiddenInput, required=False)


class TimeRecordCalendarForm(forms.Form):
    """勤務表画面のフォーム

    Args:
        forms: 継承するフォーム
    """
    username = forms.CharField(required=False)


class TimeRecordSummaryForm(forms.Form):
    """勤務集計画面のフォーム

    Args:
        forms: 継承するフォーム
    """
    pass
