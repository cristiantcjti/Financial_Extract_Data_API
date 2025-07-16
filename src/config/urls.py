from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path

from .app import api_v1

urlpatterns = [
    path("", lambda _: redirect("v1/docs", permanent=True)),
    path("admin/", admin.site.urls),
    path("api/v1/", api_v1.urls),
    path("health/", include("health_check.urls")),
]
