from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.utils.html import format_html

import timecard.settings

from . import utils
from .models import BusinessCalendar, StandardWorkPattern, TimeRecord

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

    def weekday(self, obj):
        """日付に対応する曜日文字列を取得します。

        Args:
            obj: 勤務パターンのオブジェクト

        Returns:
            str: 曜日文字列
        """
        return timecard.settings.DAY_OF_WEEK[obj.date.weekday()]

    # 設定
    weekday.short_description = '曜日'
    list_display = ['date', 'weekday', 'attendance',
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

    def has_add_permission(self, request, obj=None):
        """追加を無効化します。
        """
        return False

    def location(self, obj) -> str:
        """位置情報の表示を編集します。

        Args:
            obj: 打刻記録

        Returns:
            str: 表示情報
        """
        if obj.latitude and obj.longitude and obj.accuracy:
            if obj.accuracy < timecard.settings.MAX_ACCURACY:
                distance = utils.location_distance(obj.latitude, obj.longitude)
                if distance < timecard.settings.MAX_DISTANCE:
                    linktext = '圏内'
                else:
                    linktext = "圏外 {:,d} m (± {:,.1f} m)".format(
                        int(distance), obj.accuracy)
                url = utils.location_map_url(obj.latitude, obj.longitude)
                return format_html("<a href='{0}' target='_blank'>{1}</a>", url, linktext)
            else:
                return '低精度'
        return '不明'

    # 設定
    location.short_description = '位置情報'
    list_display = ['date', 'time', 'username',
                    'action', 'location', 'created_at', 'updated_at']
    ordering = ['date', 'time']
    list_filter = ['date']
    search_fields = ['username']
    actions = None


# 打刻記録の管理モデルを登録
admin.site.register(TimeRecord, TimeRecordAdmin)
