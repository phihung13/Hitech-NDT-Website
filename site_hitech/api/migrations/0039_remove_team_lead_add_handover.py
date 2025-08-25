from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0038_userprofile_certificates_userprofile_current_project_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leaverequest',
            name='team_lead_approval',
        ),
        migrations.RemoveField(
            model_name='leaverequest',
            name='team_lead_approved_by',
        ),
        migrations.RemoveField(
            model_name='leaverequest',
            name='team_lead_approved_at',
        ),
        migrations.RemoveField(
            model_name='leaverequest',
            name='team_lead_rejection_reason',
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='handover_approval',
            field=models.CharField(default='pending', max_length=20, verbose_name='Phê duyệt người bàn giao', choices=[('pending', 'Chờ phê duyệt'), ('approved', 'Đã duyệt'), ('rejected', 'Từ chối'), ('cancelled', 'Đã hủy')]),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='handover_approved_by',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='handover_approvals', to=settings.AUTH_USER_MODEL, verbose_name='Người bàn giao phê duyệt'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='handover_approved_at',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Thời gian phê duyệt người bàn giao'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='handover_rejection_reason',
            field=models.TextField(blank=True, verbose_name='Lý do từ chối người bàn giao'),
        ),
    ] 