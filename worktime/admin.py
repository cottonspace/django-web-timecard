"""
管理者サイトの定義です。
"""
from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.utils import dateformat

import timecard.settings
from worktime.models import (BusinessCalendar, StandardWorkPattern,
                             TimeOffPattern, TimeOffRequest, TimeRecord)
from worktime.utils import truncate_text

# Admin 画面のタイトル
AdminSite.site_header = 'システム管理'
AdminSite.site_title = 'システム管理'
AdminSite.index_title = '管理'


@admin.register(StandardWorkPattern)
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


@admin.register(TimeOffPattern)
class TimeOffPatternAdmin(admin.ModelAdmin):
    """休暇パターンの管理モデルです。

    Args:
        admin (ModelAdmin): 継承するモデル
    """

    # 設定
    list_display = [
        'id',
        'display_name',
        'attendance',
        'begin',
        'end',
        'leave',
        'back'
    ]
    ordering = ['id']
    actions = None


@admin.register(BusinessCalendar)
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
            obj: 営業日カレンダのオブジェクト

        Returns:
            str: 日付文字列
        """
        return dateformat.format(obj.date, 'Y/m/d (D)')

    # 設定
    formatted_date.short_description = '日付'
    list_display = [
        'formatted_date',
        'attendance',
        'holiday',
        'begin',
        'end',
        'leave',
        'back'
    ]
    ordering = ['date']
    list_filter = ['date']
    readonly_fields = ['date']
    actions = None


@admin.register(TimeRecord)
class TimeRecordAdmin(admin.ModelAdmin):
    """打刻記録の管理モデルです。

    Args:
        admin (ModelAdmin): 継承するモデル
    """

    def has_add_permission(self, request, obj=None):
        """追加を無効化します。
        """
        return False

    def display_username(self, obj):
        """氏名を取得します。

        Args:
            obj: 打刻記録のオブジェクト

        Returns:
            str: 氏名
        """
        return obj.display_username()

    def display_action(self, obj):
        """打刻種別の表示用文字列を取得します。

        Args:
            obj: 打刻記録のオブジェクト

        Returns:
            str: 表示用文字列
        """
        return timecard.settings.RECORD_ACTIONS.get(obj.action)

    def display_location(self, obj):
        """位置情報の表示文字列を取得します。

        Args:
            obj: 打刻記録のオブジェクト

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
    display_username.short_description = '氏名'
    display_action.short_description = '種別'
    display_location.short_description = '位置情報'
    readonly_fields = [
        'username',
        'display_username',
        'date',
        'time',
        'display_action',
        'display_location',
        'ua'
    ]
    exclude = [
        'action',
        'latitude',
        'longitude',
        'accuracy'
    ]
    list_display = [
        'date',
        'time',
        'username',
        'display_username',
        'display_action',
        'display_location',
        'created_at'
    ]
    ordering = ['date', 'time']
    list_filter = ['date']
    search_fields = ['username']
    actions = None


@admin.register(TimeOffRequest)
class TimeOffRequestAdmin(admin.ModelAdmin):
    """休暇申請の管理モデルです。

    Args:
        admin (ModelAdmin): 継承するモデル
    """

    def has_add_permission(self, request, obj=None):
        """追加を無効化します。
        """
        return False

    def display_username(self, obj):
        """氏名を取得します。

        Args:
            obj: 休暇申請のオブジェクト

        Returns:
            str: 氏名
        """
        return obj.display_username()

    def display_contact(self, obj):
        """連絡欄を取得します。

        Args:
            obj: 休暇申請のオブジェクト

        Returns:
            str: 長さを切り詰めた連絡欄の文字列
        """
        return truncate_text(obj.contact, 20, ' ...')

    # 設定
    display_username.short_description = '氏名'
    display_contact.short_description = '連絡欄'
    readonly_fields = [
        'username',
        'display_username',
        'date',
        'display_name',
        'contact',
        'attendance',
        'begin',
        'end',
        'leave',
        'back'
    ]
    list_display = [
        'date',
        'username',
        'display_username',
        'display_name',
        'accepted',
        'display_contact',
        'created_at'
    ]
    ordering = ['date', 'username']
    list_filter = ['date', 'accepted']
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
