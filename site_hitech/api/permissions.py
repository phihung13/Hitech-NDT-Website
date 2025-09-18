from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

def setup_required(view_func):
    """Decorator bắt buộc hoàn thành setup lần đầu"""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Bỏ qua kiểm tra cho trang setup chính
        if request.resolver_match and request.resolver_match.url_name == 'first_time_setup':
            return view_func(request, *args, **kwargs)
            
        # Kiểm tra profile tồn tại
        if not hasattr(request.user, 'user_profile'):
            from .models import UserProfile
            profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={
                'role': 'staff',
                'msnv': f'HTNV-{request.user.id:03d}'
            })
        else:
            profile = request.user.user_profile
            
        # Bắt buộc setup nếu chưa hoàn thành
        if getattr(profile, 'must_change_password', False) or getattr(profile, 'must_set_email', False) or not request.user.email:
            return redirect('first_time_setup')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def role_required(allowed_roles):
    """Decorator kiểm tra vai trò người dùng"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Kiểm tra setup trước
            if not hasattr(request.user, 'user_profile'):
                from .models import UserProfile
                profile, _ = UserProfile.objects.get_or_create(user=request.user, defaults={
                    'role': 'employee',
                    'msnv': f'HTNV-{request.user.id:03d}'
                })
            else:
                profile = request.user.user_profile
                
            # Bắt buộc setup nếu chưa hoàn thành (trừ trang setup)
            if request.resolver_match and request.resolver_match.url_name != 'first_time_setup':
                if getattr(profile, 'must_change_password', False) or getattr(profile, 'must_set_email', False) or not request.user.email:
                    return redirect('first_time_setup')
            
            if not hasattr(request.user, 'user_profile'):
                messages.error(request, 'Tài khoản chưa được cấu hình đầy đủ.')
                return redirect('home')
            
            user_role = request.user.user_profile.role
            if user_role not in allowed_roles:
                messages.error(request, 'Bạn không có quyền truy cập trang này.')
                return redirect('staff_login')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def permission_required(permission_name):
    """Decorator kiểm tra quyền hạn cụ thể"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request.user, 'user_profile'):
                messages.error(request, 'Tài khoản chưa được cấu hình đầy đủ.')
                return redirect('home')
            
            profile = request.user.user_profile
            if not getattr(profile, permission_name, False):
                messages.error(request, 'Bạn không có quyền thực hiện hành động này.')
                return redirect('staff_dashboard')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Shortcuts cho các vai trò (bao gồm tất cả roles)
admin_required = role_required(['admin'])
company_required = role_required(['admin', 'company'])
manager_required = role_required(['admin', 'company', 'manager'])
team_lead_required = role_required(['admin', 'company', 'manager', 'team_lead'])

# Sửa staff_required để bao gồm kiểm tra setup
def staff_required_with_setup(view_func):
    """Decorator kết hợp kiểm tra vai trò staff và setup"""
    @wraps(view_func)
    @setup_required
    @role_required(['admin', 'company', 'manager', 'team_lead', 'employee', 'employee_rd'])
    def _wrapped_view(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)
    return _wrapped_view

staff_required = staff_required_with_setup 