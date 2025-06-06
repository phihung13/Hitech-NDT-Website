from .models import Category, CourseCategory, SiteSettings

def categories(request):
    return {
        'categories': Category.objects.all(),
        'course_categories': CourseCategory.objects.all()
    }

def site_settings(request):
    # Lấy cấu hình website, nếu không có thì trả về None
    try:
        settings = SiteSettings.objects.first()
    except:
        settings = None
    
    return {
        'site_settings': settings
    }