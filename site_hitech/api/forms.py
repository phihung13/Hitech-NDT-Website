from django import forms
from .models import Post, Course, Comment
from django_ckeditor_5.widgets import CKEditor5Widget
from django.utils import timezone
from .models import Company, Equipment
from django.contrib.auth.models import User
from .models import Document, DocumentCategory, DocumentTag

class PostForm(forms.ModelForm):
    # Bỏ override content field, để Django tự động tạo từ model
    pass
    
    # SEO Fields
    meta_title = forms.CharField(
        max_length=60,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tiêu đề hiển thị trên Google (tối đa 60 ký tự)',
            'maxlength': '60'
        }),
        label='Meta Title (SEO)',
        help_text='Tiêu đề hiển thị trên kết quả tìm kiếm Google. Để trống sẽ sử dụng tiêu đề bài viết.'
    )
    
    meta_description = forms.CharField(
        max_length=160,
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Mô tả ngắn hiển thị trên Google (tối đa 160 ký tự)',
            'maxlength': '160'
        }),
        label='Meta Description (SEO)',
        help_text='Mô tả hiển thị dưới tiêu đề trên kết quả tìm kiếm Google.'
    )
    
    keywords = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'từ khóa 1, từ khóa 2, từ khóa 3',
            'data-toggle': 'tooltip',
            'title': 'Phân cách bằng dấu phẩy'
        }),
        label='Từ khóa (Keywords)',
        help_text='Các từ khóa chính của bài viết, phân cách bằng dấu phẩy.'
    )
    
    class Meta:
        model = Post
        fields = [
            'title', 'summary', 'category', 'tags', 'featured_image', 
            'content', 'meta_title', 'meta_description', 'keywords', 'published'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tiêu đề bài viết hấp dẫn',
                'required': True
            }),
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tóm tắt ngắn gọn về nội dung bài viết...'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'tags': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'featured_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Cải thiện placeholder và help text
        self.fields['category'].empty_label = "-- Chọn chuyên mục --"
        
        # Auto-fill meta fields nếu chưa có
        if self.instance and self.instance.pk:
            if not self.instance.meta_title:
                self.fields['meta_title'].widget.attrs['placeholder'] = f"Tự động: {self.instance.title[:60]}"
            if not self.instance.meta_description and self.instance.summary:
                self.fields['meta_description'].widget.attrs['placeholder'] = f"Tự động: {self.instance.summary[:160]}"

class CourseForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditor5Widget(config_name='advanced'))
    
    class Meta:
        model = Course
        fields = ['title', 'thumbnail', 'summary', 'description', 'price', 'discount_price', 'published']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }


# Thêm vào cuối file forms.py

from django import forms
from .models import ProjectFile, Project, Company, NDTMethod, Equipment
from django.contrib.auth.models import User

class ProjectFileForm(forms.ModelForm):
    class Meta:
        model = ProjectFile
        fields = ['name', 'file', 'description', 'file_type']  # Sửa từ 'file_name' thành 'name'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên file'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mô tả file'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'file_type': forms.Select(attrs={'class': 'form-select'})
        }

class ProjectUpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'location', 'methods', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'methods': forms.CheckboxSelectMultiple(),
            'status': forms.Select(attrs={'class': 'form-select'})
        }

class ProjectCreateForm(forms.ModelForm):
    # Custom fields thay thế cho company và equipment
    company_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Nhập tên công ty khách hàng'
        }),
        label='Công ty khách hàng'
    )
    
    company_address = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 2, 
            'placeholder': 'Địa chỉ công ty'
        }),
        label='Địa chỉ công ty',
        required=False
    )
    
    company_contact_person = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Tên người liên hệ'
        }),
        label='Người liên hệ',
        required=False
    )
    
    company_phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '+84 xxx xxx xxx'
        }),
        label='Số điện thoại công ty',
        required=False
    )
    
    company_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'email@company.com'
        }),
        label='Email công ty',
        required=False
    )
    
    company_tax_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Mã số thuế'
        }),
        label='Mã số thuế',
        required=False
    )
    
    equipment_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 4, 
            'placeholder': 'Nhập danh sách thiết bị cần sử dụng (mỗi thiết bị một dòng)\nVí dụ:\nMáy siêu âm UT OLYMPUS\nMáy từ tính MT MAGNAFLUX\nMáy chất thấm PT'
        }),
        label='Thiết bị sử dụng',
        help_text='Mỗi thiết bị trên một dòng riêng',
        required=False
    )
    
    # Thêm các trường bổ sung
    ndt_standards = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'VD: ASME V, AWS D1.1, ASTM E165'
        }),
        label='Tiêu chuẩn NDT áp dụng',
        required=False,
        help_text='Các tiêu chuẩn kiểm tra NDT sẽ áp dụng cho dự án'
    )
    
    client_requirements = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3, 
            'placeholder': 'Yêu cầu đặc biệt từ khách hàng'
        }),
        label='Yêu cầu khách hàng',
        required=False
    )
    
    estimated_duration = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Số ngày dự kiến',
            'min': '1'
        }),
        label='Thời gian dự kiến (ngày)',
        required=False,
        help_text='Số ngày dự kiến hoàn thành dự án'
    )
    
    priority_level = forms.ChoiceField(
        choices=[
            ('low', 'Thấp'),
            ('normal', 'Bình thường'),
            ('high', 'Cao'),
            ('urgent', 'Khẩn cấp')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Mức độ ưu tiên',
        initial='normal'
    )
    
    budget_range = forms.ChoiceField(
        choices=[
            ('under_50m', 'Dưới 50 triệu'),
            ('50m_100m', '50-100 triệu'), 
            ('100m_500m', '100-500 triệu'),
            ('500m_1b', '500 triệu - 1 tỷ'),
            ('over_1b', 'Trên 1 tỷ'),
            ('negotiable', 'Thỏa thuận')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Phạm vi ngân sách',
        required=False
    )
    
    risk_assessment = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3, 
            'placeholder': 'Đánh giá rủi ro và biện pháp phòng ngừa'
        }),
        label='Đánh giá rủi ro',
        required=False
    )
    
    special_requirements = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3, 
            'placeholder': 'Các yêu cầu đặc biệt về an toàn, môi trường, thời gian làm việc...'
        }),
        label='Yêu cầu đặc biệt',
        required=False
    )
    
    class Meta:
        model = Project
        # Bao gồm tất cả các trường cần thiết
        fields = [
            'name', 'code', 'description', 'location', 
            'start_date', 'end_date', 'status', 
            'project_manager', 'methods', 'staff', 'contract_value'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Tên dự án NDT'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Mã dự án tự do (VD: PROJ-001, DT-2024-001, ...)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Mô tả chi tiết về phạm vi công việc, vật liệu kiểm tra, phương pháp sử dụng...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Địa điểm thực hiện dự án'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'project_manager': forms.Select(attrs={'class': 'form-select'}),
            'methods': forms.CheckboxSelectMultiple(),
            'staff': forms.CheckboxSelectMultiple(),
            'contract_value': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Giá trị hợp đồng (VND)', 
                'step': '1000'
            })
        }
        labels = {
            'name': 'Tên dự án',
            'code': 'Mã dự án', 
            'description': 'Mô tả dự án',
            'location': 'Địa điểm thực hiện',
            'start_date': 'Ngày bắt đầu',
            'end_date': 'Ngày kết thúc dự kiến',
            'status': 'Trạng thái dự án',
            'project_manager': 'Quản lý dự án',
            'methods': 'Phương pháp NDT',
            'staff': 'Nhân viên tham gia',
            'contract_value': 'Giá trị hợp đồng (VND)'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set queryset cho project_manager (chỉ admin và manager)
        self.fields['project_manager'].queryset = User.objects.filter(
            user_profile__role__in=['manager', 'admin']
        ).select_related('user_profile')
        
        # Set queryset cho staff (chỉ staff)
        self.fields['staff'].queryset = User.objects.filter(
            user_profile__role='staff'
        ).select_related('user_profile')
        
        # Cải thiện hiển thị cho các field
        self.fields['project_manager'].empty_label = "-- Chọn quản lý dự án --"
        
        # Custom label cho staff và methods
        for field_name in ['staff', 'methods']:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'class': 'form-check-input'
                })
        
        # Placeholder đơn giản cho mã dự án
        self.fields['code'].widget.attrs['placeholder'] = "Nhập mã dự án của bạn"
    
    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if not company_name or not company_name.strip():
            raise forms.ValidationError('Tên công ty không được để trống')
        return company_name.strip()
    
    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            raise forms.ValidationError('Mã dự án không được để trống')
        
        # Chỉ kiểm tra độ dài và ký tự hợp lệ
        if len(code.strip()) < 3:
            raise forms.ValidationError('Mã dự án phải có ít nhất 3 ký tự')
        
        return code.strip().upper()
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Kiểm tra logic ngày
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError('Ngày kết thúc phải sau ngày bắt đầu')
            
            from datetime import timedelta
            if (end_date - start_date).days > 365:
                raise forms.ValidationError('Thời gian dự án không nên quá 1 năm')
        
        return cleaned_data
    
    def save(self, commit=True):
        # Tạo instance nhưng chưa save vào DB
        project = super().save(commit=False)
        
        # Xử lý company
        company_name = self.cleaned_data['company_name']
        company_data = {
            'name': company_name,
            'address': self.cleaned_data.get('company_address', 'Chưa cập nhật'),
            'contact_person': self.cleaned_data.get('company_contact_person', 'Chưa cập nhật'),
            'phone': self.cleaned_data.get('company_phone', 'Chưa cập nhật'),
            'email': self.cleaned_data.get('company_email', 'info@company.com'),
            'tax_code': self.cleaned_data.get('company_tax_code', '')
        }
        
        # Tạo mã công ty nếu chưa có
        company, created = Company.objects.get_or_create(
            name=company_name,
            defaults={
                **company_data,
                'code': f'COMP-{timezone.now().strftime("%Y%m%d")}-{Company.objects.count() + 1:03d}'
            }
        )
        
        # Nếu công ty đã tồn tại, cập nhật thông tin mới
        if not created:
            for key, value in company_data.items():
                if value and value != 'Chưa cập nhật':
                    setattr(company, key, value)
            company.save()
        
        project.company = company
        
        if commit:
            project.save()
            # Save many-to-many relationships
            self.save_m2m()
            
            # Xử lý equipment nếu có
            equipment_text = self.cleaned_data.get('equipment_text')
            if equipment_text:
                equipment_lines = [line.strip() for line in equipment_text.split('\n') if line.strip()]
                
                for equipment_name in equipment_lines:
                    equipment, created = Equipment.objects.get_or_create(
                        name=equipment_name,
                        defaults={
                            'model': 'Chưa cập nhật',
                            'serial_number': f'SN-{timezone.now().strftime("%Y%m%d")}-{Equipment.objects.count() + 1:04d}',
                            'manufacturer': 'Chưa cập nhật',
                            'calibration_date': timezone.now().date(),
                            'next_calibration': timezone.now().date() + timezone.timedelta(days=365),
                            'status': 'active'
                        }
                    )
                    project.equipment.add(equipment)
        
        return project

# Document Management Forms
class DocumentForm(forms.ModelForm):
    """Form upload và chỉnh sửa tài liệu"""
    tags = forms.ModelMultipleChoiceField(
        queryset=DocumentTag.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Tags'
    )
    
    class Meta:
        model = Document
        fields = [
            'title', 'category', 'description', 'file', 'tags', 'version'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tiêu đề tài liệu...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Mô tả tài liệu...'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.jpg,.jpeg,.png,.zip,.rar'
            }),
            'version': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '1.0'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = DocumentCategory.objects.filter(is_active=True)
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Kiểm tra kích thước file (tối đa 50MB)
            if file.size > 50 * 1024 * 1024:
                raise forms.ValidationError('File không được vượt quá 50MB')
            
            # Kiểm tra định dạng file
            allowed_extensions = [
                'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 
                'txt', 'jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'zip', 'rar'
            ]
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(f'Định dạng file không được hỗ trợ. Chỉ chấp nhận: {", ".join(allowed_extensions)}')
        
        return file
    
    def save(self, commit=True):
        document = super().save(commit=False)
        
        if not document.document_code:
            # Tự động tạo mã tài liệu
            category_code = document.category.slug.upper()[:3]
            last_doc = Document.objects.filter(
                document_code__startswith=category_code
            ).order_by('-id').first()
            
            if last_doc and last_doc.document_code:
                try:
                    last_num = int(last_doc.document_code.split('-')[-1])
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1
                
            document.document_code = f"{category_code}-{new_num:03d}"
        
        # Đặt access_level mặc định là 'internal' (nội bộ)
        document.access_level = 'internal'
        document.allowed_roles = ''
        
        if commit:
            document.save()
            self.save_m2m()
        
        return document

class DocumentCategoryForm(forms.ModelForm):
    """Form tạo/chỉnh sửa danh mục tài liệu"""
    class Meta:
        model = DocumentCategory
        fields = ['name', 'description', 'icon', 'parent', 'order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tên danh mục...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'fas fa-folder'
            }),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            })
        }

class DocumentTagForm(forms.ModelForm):
    """Form tạo/chỉnh sửa tag tài liệu"""
    class Meta:
        model = DocumentTag
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tên tag...'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color'
            })
        }

class DocumentSearchForm(forms.Form):
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tìm kiếm tài liệu...'
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=DocumentCategory.objects.all(),
        required=False,
        empty_label="Tất cả danh mục",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=DocumentTag.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )