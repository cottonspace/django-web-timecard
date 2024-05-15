"""
Django プロジェクト timecard の WSGI 定義です。
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timecard.settings')

application = get_wsgi_application()
