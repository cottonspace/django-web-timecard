from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.utils import dateformat

import timecard.settings
import worktime.utils

from .models import (BusinessCalendar, StandardWorkPattern, TimeOffPattern,
                     TimeOffRequest, TimeRecord)

# Admin 画面のタイトル
AdminSite.site_header = 'Web タイムカード管理'
AdminSite.site_title = 'Web タイムカード管理'
AdminSite.index_title = '管理'


class StandardWorkPatternAdmin(admin.ModelAdmin):
    """勤務パターンの管理モデルです。

    Args:
        admin (ModelAdmin): 継承するモデル
    """

    def has_add_permission(self, request, obj=None):
        """追加を無効化します。
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """削除を無効化します。
        """
        return False

    def weekday(self, obj) -> str:
        """登録 ID に対応する曜日文字列を取得します。

        Args:
            obj: 勤務パターンのオブジェクト

        Returns:
            str: 曜日文字列
        """
        return timecard.settings.DAY_OF_WEEK[obj.id]

    # 設定
    weekday.short_description = '曜日'
    list_display = ['weekday', 'attendance', 'begin', 'end', 'leave', 'back']
    ordering = ['id']
    actions = None


# 勤務パターンの管理モデルを登録
admin.site.register(StandardWorkPattern, StandardWorkPatternAdmin)


class TimeOffPatternAdmin(admin.ModelAdmin):
    """休暇パターンの管理モデルです。

    Args:
        admin (ModelAdmin): 継承するモデル
    """

    # 設定
    list_display = ['id', 'display_name',
                    'attendance', 'begin', 'end', 'leave', 'back']
    ordering = ['id']
    actions = None


# 休暇パターンの管理モデルを登録
admin.site.register(TimeOffPattern, TimeOffPatternAdmin)


class BusinessCalendarAdmin(admin.ModelAdmin):
    """営業日カレンダの管理モデルです。

    Args:
        admin (ModelAdmin): 継承するモデル
    """

    def has_add_permission(self, request, obj=None):
        """追加を無効化します。
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """削除を無効化します。
        """
        return False

    def formatted_date(self, obj):
        """フォーマット指定した日付文字列を取得します。

        Args:
            obj: 勤務パターンのオブジェクト

        Returns:
            str: 日付文字列
        """
        return dateformat.format(obj.date, 'Y/m/d (D)')

    # 設定
    formatted_date.short_description = '日付'
    list_display = ['formatted_date', 'attendance',
                    'holiday', 'begin', 'end', 'leave', 'back']
    ordering = ['date']
    list_filter = ['date']
    readonly_fields = ['date']
    actions = None


# 営業日カレンダの管理モデルを登録
admin.site.register(BusinessCalendar, BusinessCalendarAdmin)


class TimeRecordAdmin(admin.ModelAdmin):
    """打刻記録の管理モデルです。

    Args:
        admin (ModelAdmin): 継承するモデル
    """

    def __init__(self, *args, **kwargs):
        """インスタンスを初期化します。
        """
        super().__init__(*args, **kwargs)
        self.users = worktime.utils.get_users(False)

    def has_add_permission(self, request, obj=None):
        """追加を無効化します。
        """
        return False

    def formatted_date(self, obj):
        """フォーマット指定した日付文字列を取得します。

        Args:
            obj: 勤務パターンのオブジェクト

        Returns:
            str: 日付文字列
        """
        return dateformat.format(obj.date, 'Y/m/d (D)')

    def display_action(self, obj):
        """打刻種別の表示用文字列を取得します。

        Args:
            obj: 勤務パターンのオブジェクト

        Returns:
            str: 表示用文字列
        """
        if obj.action == 'begin':
            return '出勤'
        elif obj.action == 'end':
            return '退勤'
        return None

    def display_username(self, obj):
        """氏名を取得します。

        Args:
            obj: 勤務パターンのオブジェクト

        Returns:
            str: 氏名文字列
        """
        return self.users.get(obj.username, obj.username)

    def display_location(self, obj):
        """位置情報の表示文字列を取得します。

        Args:
            obj: 打刻情報のオブジェクト

        Returns:
            str: 位置情報
        """
        return obj.location()

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """詳細画面に拡張コンテキストを追加します。

        Args:
            request: リクエスト情報
            object_id: オブジェクト ID
            form_url: フォーム URL (デフォルトは "")
            extra_context: 拡張コンテキスト (デフォルトは None)

        Returns:
            拡張コンテキストを適用したレスポンス
        """
        extra_context = extra_context or {}
        extra_context['LOCATION_ORIGIN'] = timecard.local_settings.LOCATION_ORIGIN
        extra_context['MAX_DISTANCE'] = timecard.local_settings.MAX_DISTANCE
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    # 設定
    formatted_date.short_description = '日付'
    display_action.short_description = '種別'
    display_username.short_description = '氏名'
    display_location.short_description = '位置情報'
    readonly_fields = ['date', 'time', 'username', 'display_username',
                       'display_action', 'latitude', 'longitude', 'accuracy', 'ua']
    exclude = ['action']
    list_display = ['formatted_date', 'time', 'display_username',
                    'display_action', 'display_location', 'created_at']
    ordering = ['date', 'time']
    list_filter = ['date']
    search_fields = ['username']
    actions = None


# 打刻記録の管理モデルを登録
admin.site.register(TimeRecord, TimeRecordAdmin)


class TimeOffRequestAdmin(admin.ModelAdmin):
    """休暇申請の管理モデルです。

    Args:
        admin (ModelAdmin): 継承するモデル
    """

    def __init__(self, *args, **kwargs):
        """インスタンスを初期化します。
        """
        super().__init__(*args, **kwargs)
        self.users = worktime.utils.get_users(False)

    def has_add_permission(self, request, obj=None):
        """追加を無効化します。
        """
        return False

    def formatted_date(self, obj):
        """フォーマット指定した日付文字列を取得します。

        Args:
            obj: 勤務パターンのオブジェクト

        Returns:
            str: 日付文字列
        """
        return dateformat.format(obj.date, 'Y/m/d (D)')

    def display_username(self, obj):
        """氏名を取得します。

        Args:
            obj: 勤務パターンのオブジェクト

        Returns:
            str: 氏名文字列
        """
        return self.users.get(obj.username, obj.username)

    # 設定
    formatted_date.short_description = '日付'
    display_username.short_description = '氏名'
    readonly_fields = ['date', 'username', 'display_username',
                       'display_name', 'attendance', 'begin', 'end', 'leave', 'back']
    list_display = ['formatted_date', 'display_username',
                    'display_name', 'accepted', 'created_at']
    ordering = ['date', 'username']
    list_filter = ['date', 'username', 'accepted']
    search_fields = ['username']
    actions = ['action_accept']

    def action_accept(self, request, queryset):
        """選択したレコードを一括で承認します。

        Args:
            request: リクエスト情報
            queryset: 選択されたレコード
        """
        queryset.update(accepted=True)

    action_accept.short_description = '選択された 休暇申請 の承認'


# 休暇申請の管理モデルを登録
admin.site.register(TimeOffRequest, TimeOffRequestAdmin)
