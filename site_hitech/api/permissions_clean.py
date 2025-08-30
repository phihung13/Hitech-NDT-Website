from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponseForbidden

def role_required(allowed_roles):
    """Decorator kiểm tra vai trò người dùng"""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if not hasattr(request.user, 'user_profile'):
                messages.error(request, 'Tài khoản chưa được cấu hình đầy đủ.')
                return redirect('home')
            
            user_role = request.user.user_profile.role
            if user_role not in allowed_roles:
                messages.error(request, 'Bạn không có quyền truy cập trang này.')
                return redirect('staff_dashboard')
            
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
staff_required = role_required(['admin', 'company', 'manager', 'team_lead', 'staff']) 