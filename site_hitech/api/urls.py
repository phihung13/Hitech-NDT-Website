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

# Import thêm
# from .report_views import (
#     report_dashboard, project_report, thickness_report
# )

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
    path('contact/', contact, name='contact'),
    
    # Staff authentication và dashboard
    path('staff/login/', views.staff_login, name='staff_login'),
    path('staff/logout/', views.staff_logout, name='staff_logout'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    
    # Project management
    path('projects/create/', views.create_project, name='create_project'),
    path('project/<int:project_id>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/upload/', views.upload_file, name='upload_file'),
    path('project/<int:project_id>/download/<int:file_id>/', views.download_file, name='download_file'),
    path('project/<int:project_id>/update/', views.update_project, name='update_project'),
    path('project/<int:project_id>/progress/', views.update_progress, name='update_progress'),
    
    # Admin và Manager dashboard
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.user_management, name='user_management'),
    
    # Post management với phân quyền
    path('posts/publish/<int:post_id>/', views.publish_post, name='publish_post'),
    path('posts/delete/<int:post_id>/', views.delete_post, name='delete_post'),
    
    # Báo cáo - Tạm thời comment out
    # path('reports/', report_dashboard, name='report_dashboard'),
    # path('reports/projects/', project_report, name='project_report'),
    # path('reports/thickness/', thickness_report, name='thickness_report'),
    # path('reports/welds/', weld_report, name='weld_report'),
]
