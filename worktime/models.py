from django.core.exceptions import ValidationError
from django.db import models
from geopy.distance import geodesic

import timecard.settings


class StandardWorkPattern(models.Model):
    """勤務パターンのモデルです。

    Args:
        models: 継承するモデル

    Raises:
        ValidationError: 値の不正

    Returns:
        str: 文字列表現
    """
    id = models.IntegerField('曜日', primary_key=True)
    attendance = models.BooleanField('営業日', default=True)
    begin = models.TimeField('勤務開始', blank=True, null=True)
    end = models.TimeField('勤務終了', blank=True, null=True)
    leave = models.TimeField('休憩開始', blank=True, null=True)
    back = models.TimeField('休憩終了', blank=True, null=True)

    def clean(self):
        """値の検査

        Raises:
            ValidationError: 値の不正
        """
        if self.attendance:
            if (not self.begin) or (not self.end):
                raise ValidationError("営業日は勤務開始と勤務終了の時刻は必須です。")
        else:
            if self.begin or self.end or self.leave or self.back:
                raise ValidationError("非営業日は時刻の指定は出来ません。")

    def __str__(self):
        """文字列表現を取得します。

        Returns:
            str: 文字列表現
        """
        return timecard.settings.DAY_OF_WEEK[self.id]

    class Meta:
        """メタ情報です。
        """
        verbose_name = "勤務パターン"
        verbose_name_plural = "勤務パターン"


class BusinessCalendar(models.Model):
    """営業日カレンダのモデルです。

    Args:
        models: 継承するモデル

    Raises:
        ValidationError: 値の不正

    Returns:
        str: 文字列表現
    """
    date = models.DateField('日付', primary_key=True)
    attendance = models.BooleanField('営業日')
    holiday = models.CharField('休業理由', max_length=40, blank=True)
    begin = models.TimeField('勤務開始', blank=True, null=True)
    end = models.TimeField('勤務終了', blank=True, null=True)
    leave = models.TimeField('休憩開始', blank=True, null=True)
    back = models.TimeField('休憩終了', blank=True, null=True)

    def clean(self):
        """値の検査

        Raises:
            ValidationError: 値の不正
        """
        if self.attendance:
            if self.holiday:
                raise ValidationError("営業日は休業理由は入力できません。")
            if (not self.begin) or (not self.end):
                raise ValidationError("営業日は勤務開始と勤務終了の時刻は必須です。")
        else:
            if not self.holiday:
                raise ValidationError("非営業日は休業理由を入力してください。")
            if self.begin or self.end or self.leave or self.back:
                raise ValidationError("非営業日は時刻の指定は出来ません。")

    def __str__(self):
        """文字列表現を取得します。

        Returns:
            str: 文字列表現
        """
        return self.date.strftime('%Y-%m-%d (%a)')

    class Meta:
        """メタ情報です。
        """
        verbose_name = "営業日"
        verbose_name_plural = "営業日"


class TimeRecord(models.Model):
    """打刻情報のモデルです。

    Args:
        models: 継承するモデル

    Returns:
        str: 文字列表現
    """
    id = models.AutoField('ID', primary_key=True)
    date = models.DateField('日付')
    time = models.TimeField('時刻')
    username = models.CharField('ユーザー名', max_length=150)
    action = models.CharField('種別', max_length=20)
    latitude = models.FloatField('緯度', blank=True, null=True)
    longitude = models.FloatField('経度', blank=True, null=True)
    accuracy = models.FloatField('誤差', blank=True, null=True)
    ua = models.TextField('ブラウザ情報', max_length=400, blank=True, null=True)
    created_at = models.DateTimeField('作成日時', auto_now_add=True)
    updated_at = models.DateTimeField('更新日時', auto_now=True)

    def __str__(self):
        """文字列表現を取得します。

        Returns:
            str: 文字列表現
        """
        return self.date.strftime('%Y-%m-%d (%a)') + ' ' + self.username

    def location(self) -> str:
        """位置情報の表示を編集します。

        Returns:
            str: 表示情報
        """
        if self.latitude and self.longitude and self.accuracy:
            if self.accuracy < timecard.settings.MAX_ACCURACY:
                distance = geodesic(
                    timecard.settings.LOCATION_ORIGIN, (self.latitude, self.longitude)).m
                if distance < timecard.settings.MAX_DISTANCE:
                    return '圏内'
                else:
                    return "圏外 {:,d} m (± {:,.1f} m)".format(int(distance), self.accuracy)
            else:
                return '低精度'
        return None

    class Meta:
        """メタ情報です。
        """
        verbose_name = "打刻記録"
        verbose_name_plural = "打刻記録"
