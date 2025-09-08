from django.urls import path
from . import views

from rest_framework_simplejwt.views import TokenRefreshView
from .auth_views import register, login
from django.urls import path
from .views import (
    home, blog_list, blog_detail,
    course_list, course_detail,
    create_post, create_course,
    about, contact,
    # search, profile_view, edit_profile,
    # document_list, document_detail, document_upload, document_delete,
    service_list, service_detail, # service_category,
    project_list, project_detail, create_project, project_management_detail,
    edit_project_file, delete_project_file,
    # public_project_detail, report_list, generate_report,
    staff_dashboard, change_language
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
    path('lien-he/', contact, name='contact'),
    # path('tim-kiem/', search, name='search'),
    
    # User profiles
    # path('profile/', profile_view, name='profile'),
    # path('profile/edit/', edit_profile, name='edit_profile'),
    
    # Document paths
    # path('tai-lieu/', document_list, name='document_list'),
    # path('tai-lieu/<int:document_id>/', document_detail, name='document_detail'),
    # path('tai-lieu/upload/', document_upload, name='document_upload'),
    # path('tai-lieu/<int:document_id>/delete/', document_delete, name='document_delete'),
    
    # Service paths
    path('dich-vu/', service_list, name='service_list'),
    path('dich-vu/<slug:slug>/', service_detail, name='service_detail'),
    # path('dich-vu/danh-muc/<slug:category_slug>/', service_category, name='service_category'),
    
    # Project paths
    path('du-an/', project_list, name='project_list'),
    path('du-an/<int:project_id>/', project_management_detail, name='project_detail'),
    path('projects/create/', create_project, name='create_project'),
    # path('du-an/cong-khai/<int:project_id>/', public_project_detail, name='public_project_detail'),
    
    # Reports
    # path('reports/', report_list, name='report_list'),
    # path('reports/generate/', generate_report, name='generate_report'),
    
    # Staff dashboard
    path('dashboard/', staff_dashboard, name='staff_dashboard'),
    
    # Language change
    path('change-language/', change_language, name='change_language'),
    
    # Staff authentication và dashboard
    path('staff/login/', views.staff_login, name='staff_login'),
    path('staff/logout/', views.staff_logout, name='staff_logout'),
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    
    # ERP Module URLs - tất cả có prefix dashboard/
    path('dashboard/', views.dashboard_overview, name='dashboard_overview'),
    path('dashboard/projects/', views.projects_management, name='projects_management'),
    path('dashboard/staff/', views.staff_management, name='staff_management'),
    path('dashboard/staff/export/', views.export_staff_data, name='export_staff_data'),
    path('dashboard/attendance/', views.attendance_management, name='attendance_management'),
    path('dashboard/equipment/', views.equipment_management, name='equipment_management'),
    path('dashboard/documents/', views.documents_management, name='documents_management'),
    path('documents/upload/', views.document_upload, name='document_upload'),
    path('documents/<slug:slug>/', views.document_detail, name='document_detail'),
    path('documents/<slug:slug>/download/', views.document_download, name='document_download'),
    path('documents/<slug:slug>/edit/', views.document_edit, name='document_edit'),
    path('documents/<slug:slug>/delete/', views.document_delete, name='document_delete'),
    path('documents/<slug:slug>/share/', views.document_share, name='document_share'),
    path('manage/categories/', views.manage_categories, name='manage_categories'),
    path('manage/tags/', views.manage_tags, name='manage_tags'),
    path('dashboard/quality/', views.quality_management, name='quality_management'),
    
    # Export attendance data
    path('export/attendance/', views.export_attendance_data, name='export_attendance_data'),
    path('dashboard/analytics/', views.analytics_management, name='analytics_management'),
    
    # Project management
    path('project/<int:project_id>/upload/', views.upload_file, name='upload_file'),
    path('project/<int:project_id>/download/<int:file_id>/', views.download_file, name='download_file'),
    path('project/<int:project_id>/update/', views.update_project, name='update_project'),
    path('project/<int:project_id>/progress/', views.update_progress, name='update_progress'),
    path('project/<int:project_id>/file/<int:file_id>/edit/', views.edit_project_file, name='edit_project_file'),
    path('project/<int:project_id>/file/<int:file_id>/delete/', views.delete_project_file, name='delete_project_file'),
    
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
    path('dich-vu/', views.service_list, name='service_list'),
    path('dich-vu/<slug:slug>/', views.service_detail, name='service_detail'),
    
    # Project public URLs (blog-style)
    path('dich-vu/du-an/', views.project_list, name='public_project_list'),
    path('dich-vu/du-an/<slug:slug>/', views.project_detail, name='public_project_detail'),
    
    path('phan-cong-nhan-vien/', views.phan_cong_nhan_vien, name='phan_cong_nhan_vien'),
    path('staff/assign/', views.staff_assign, name='staff_assign'),
    path('equipment/schedule/', views.equipment_schedule, name='equipment_schedule'),
    path('reports/generate/', views.report_generate, name='report_generate'),
    
    # NDT Methods Management
    path('manage/ndt-methods/', views.ndt_methods_management, name='ndt_methods_management'),
    path('manage/ndt-methods/create/', views.create_ndt_method, name='create_ndt_method'),
    path('manage/ndt-methods/delete/<int:method_id>/', views.delete_ndt_method, name='delete_ndt_method'),
    path('manage/ndt-methods/create-defaults/', views.create_default_ndt_methods, name='create_default_ndt_methods'),

    # Leave request APIs
    path('api/leave-requests/create/', views.create_leave_request, name='create_leave_request'),
    path('api/leave-requests/', views.get_leave_requests, name='get_leave_requests'),
    path('api/leave-requests/approve/', views.approve_leave_request, name='approve_leave_request'),
    path('api/leave-requests/<int:request_id>/delete/', views.delete_leave_request, name='delete_leave_request'),
    path('api/users/handovers/', views.get_handover_candidates, name='get_handover_candidates'),
    path('api/notifications/', views.get_system_notifications, name='get_system_notifications'),
    
    # Attendance URLs
    path('api/attendance/save/', views.save_attendance_data, name='save_attendance_data'),
    path('api/attendance/update/<str:date>/', views.update_attendance_data, name='update_attendance_data'),
    path('api/attendance/delete/<str:date>/', views.delete_attendance_data, name='delete_attendance_data'),
    path('api/attendance/', views.get_attendance_data, name='get_attendance_data'),
    path('api/attendance/export/', views.export_attendance_data, name='export_attendance_data'),
    path('api/attendance/export-json/', views.export_attendance_json, name='export_attendance_json'),
]
