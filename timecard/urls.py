"""
Django プロジェクト timecard の URL ディスパッチャです。
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/worktime/login/', permanent=False)),
    path('admin/', admin.site.urls),
    path('worktime/', include('worktime.urls')),
]
