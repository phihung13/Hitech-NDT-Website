# Generated manually

from django.db import migrations, models


def update_file_types(apps, schema_editor):
    Document = apps.get_model('api', 'Document')
    
    # Update existing documents with file type
    for doc in Document.objects.all():
        if doc.file:
            try:
                ext = doc.file.name.split('.')[-1].lower()
                doc.file_type = ext
                doc.save()
            except:
                doc.file_type = ''
                doc.save()


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0048_create_document_access_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='file_type',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.RunPython(update_file_types),
    ] 