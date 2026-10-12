from django.contrib import admin
from django.urls import path, re_path

from core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("admin/", admin.site.urls),
    re_path(r"^media/(?P<path>.*)$", views.media),
]
