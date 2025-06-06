from django.urls import path
from . import views

from rest_framework_simplejwt.views import TokenRefreshView
from .auth_views import register, login
from django.urls import path
from .views import (
    home, blog_list, blog_detail,
    course_list, course_detail,
    create_post, create_course,
    about, contact
)

urlpatterns = [
    # # API endpoints đặt dưới /api
    # path('api/bai-viet/', views.blog_list, name='api_blog_list'),
    # path('api/bai-viet/<slug:slug>/', views.blog_detail, name='api_blog_detail'),
    # path('api/khoa-hoc/', views.course_list, name='api_course_list'),
    # path('api/khoa-hoc/<slug:slug>/', views.course_detail, name='api_course_detail'),
    
    # Xác thực
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Frontend routes
    path('', home, name='home'),
    path('bai-viet/', blog_list, name='blog_list'),
    path('bai-viet/<slug:slug>/', blog_detail, name='blog_detail'),
    path('khoa-hoc/', course_list, name='course_list'),
    path('khoa-hoc/<slug:slug>/', course_detail, name='course_detail'),
    path('tao-bai-viet/', create_post, name='create_post'),
    path('tao-khoa-hoc/', create_course, name='create_course'),
    path('gioi-thieu/', about, name='about'),
    path('lien-he/', contact, name='contact'),
    
    # Admin customization đã được chuyển sang api.admin_urls
]
