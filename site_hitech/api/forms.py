from django import forms
from .models import Post, Course, Comment
from ckeditor.widgets import CKEditorWidget
from django.utils import timezone
from .models import Company, Equipment
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Post
        fields = ['title', 'category', 'featured_image', 'summary', 'content', 'published']

class CourseForm(forms.ModelForm):
    description = forms.CharField(widget=CKEditorWidget())
    
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
            'placeholder': 'Nhập tên công ty'
        }),
        label='Công ty'
    )
    
    equipment_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 3, 
            'placeholder': 'Nhập danh sách thiết bị (mỗi thiết bị một dòng)'
        }),
        label='Thiết bị sử dụng',
        help_text='Mỗi thiết bị trên một dòng riêng'
    )
    
    class Meta:
        model = Project
        # Chỉ include các field cần thiết, loại bỏ company và equipment gốc
        fields = [
            'name', 'code', 'description', 'location', 
            'start_date', 'end_date', 'status', 
            'project_manager', 'methods', 'staff', 'contract_value'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Tên dự án'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Mã dự án (VD: NDT-2024-001)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Mô tả chi tiết dự án'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Địa điểm thực hiện'
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
                'step': '0.01'
            })
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
    
    def clean_company_name(self):
        company_name = self.cleaned_data.get('company_name')
        if not company_name or not company_name.strip():
            raise forms.ValidationError('Tên công ty không được để trống')
        return company_name.strip()
    
    def clean_equipment_text(self):
        equipment_text = self.cleaned_data.get('equipment_text')
        if not equipment_text or not equipment_text.strip():
            raise forms.ValidationError('Danh sách thiết bị không được để trống')
        return equipment_text.strip()
    
    def save(self, commit=True):
        # Tạo instance nhưng chưa save vào DB
        project = super().save(commit=False)
        
        # Xử lý company
        company_name = self.cleaned_data['company_name']
        company, created = Company.objects.get_or_create(
            name=company_name,
            defaults={
                'code': f'COMP-{timezone.now().strftime("%Y%m%d")}-{Company.objects.count() + 1:03d}',
                'address': 'Chưa cập nhật',
                'contact_person': 'Chưa cập nhật',
                'phone': 'Chưa cập nhật',
                'email': 'info@company.com'
            }
        )
        project.company = company
        
        if commit:
            project.save()
            # Save many-to-many relationships
            self.save_m2m()
            
            # Xử lý equipment
            equipment_text = self.cleaned_data['equipment_text']
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