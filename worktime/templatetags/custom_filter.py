import json
from decimal import Decimal

from django import template

# テンプレートのフィルタライブラリ
register = template.Library()


@register.filter(name='dict_value')
def dict_value(d, key):
    """dict の値を取得するフィルタです。

    Args:
        d (dict): 参照する dict
        k (Any): 参照するキー

    Returns:
        Any: 取得された値
    """
    if (key in d.keys()):
        return d[key]
    return None


def dump_default(obj) -> object:
    """JSON シリアライズできない型を変換します。

    Args:
        obj (Any): オブジェクト

    Raises:
        TypeError: 対応していない型の場合

    Returns:
        object: 変換後の値
    """
    if isinstance(obj, Decimal):
        if int(obj) == obj:
            return int(obj)
        else:
            return float(obj)
    raise TypeError


@register.filter(name='json_dumps')
def json_dumps(obj) -> str:
    """オブジェクトを JSON 文字列にシリアライズするフィルタです。

    Args:
        obj (Any): オブジェクト

    Returns:
        str: JSON 文字列
    """
    return json.dumps(obj, default=dump_default)
