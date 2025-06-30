"""
URL configuration for site_hitech project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language

urlpatterns = [
    path('set_language/', set_language, name='set_language'),
]

urlpatterns += i18n_patterns(
    path('admin/customization/', include('api.admin_urls', namespace='api_admin')),  # Thêm URLs cho trang tùy chỉnh admin
    path('admin/', admin.site.urls),
    path('', include('api.urls')),  # Thay thế 'api/' bằng '' để loại bỏ tiền tố
    path('blog/', include('blog.urls')),
    path('summernote/', include('django_summernote.urls')),  # Thêm URL cho Summernote
    path('ckeditor/', include('ckeditor_uploader.urls')),  # Thêm URL cho CKEditor upload
    path('ckeditor5/', include('django_ckeditor_5.urls')),  # Thêm URL cho CKEditor5
    prefix_default_language=False,
)

# Thêm URLs cho media files trong development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
