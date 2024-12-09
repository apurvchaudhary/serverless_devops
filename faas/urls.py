from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import RedirectView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("functions.urls")),
    path("favicon.ico", RedirectView.as_view(url="/static/images/devops.png")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
