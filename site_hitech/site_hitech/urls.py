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
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/', include('api.urls')),
#     path('', views.home, name='home'),
#     path('courses/', views.course_list, name='course_list'),
#     path('courses/<int:id>/', views.course_detail, name='course_detail'),
#     path('posts/', views.post_list, name='post_list'),
#     path('posts/<int:id>/', views.post_detail, name='post_detail'),
#     path('about/', views.about, name='about'),  # 👈 Thêm trang giới thiệu
#     path('contact/', views.contact, name='contact'),  # 👈 Thêm trang liên hệ
# ]


urlpatterns = [
    path('admin/customization/', include('api.admin_urls', namespace='api_admin')),  # Thêm URLs cho trang tùy chỉnh admin
    path('admin/', admin.site.urls),
    path('', include('api.urls')),  # Thay thế 'api/' bằng '' để loại bỏ tiền tố
    path('blog/', include('blog.urls')),
]

# Thêm URLs cho media files trong development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
