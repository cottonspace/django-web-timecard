from django import template

# テンプレートのフィルタライブラリ
register = template.Library()


@register.filter(name='dict_value')
def dict_value(d, k):
    """dict の値を取得するフィルタです。

    Args:
        d (dict): 参照する dict
        k (Any): 参照するキー

    Returns:
        Any: 取得された値
    """
    if (k in d.keys()):
        return d[k]
    else:
        return None
