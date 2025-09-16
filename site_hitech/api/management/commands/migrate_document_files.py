from django.core.management.base import BaseCommand
from api.models import Document, DocumentFileVersion
from django.contrib.auth.models import User
from django.db.models import Count

class Command(BaseCommand):
    help = 'Migrate existing documents to DocumentFileVersion'

    def handle(self, *args, **options):
        # Xóa tất cả dữ liệu cũ trong DocumentFileVersion
        DocumentFileVersion.objects.all().delete()
        self.stdout.write('Cleared old DocumentFileVersion data')
        
        # Tìm các Document trùng lặp theo title
        duplicate_titles = Document.objects.values('title').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        self.stdout.write(f'Found {len(duplicate_titles)} duplicate titles')
        
        # Xử lý từng nhóm trùng lặp
        for item in duplicate_titles:
            title = item['title']
            docs = Document.objects.filter(title=title).order_by('created_at')
            
            self.stdout.write(f'Processing duplicates for "{title}": {docs.count()} documents')
            
            # Giữ lại Document đầu tiên (cũ nhất)
            main_doc = docs.first()
            
            # Tạo DocumentFileVersion cho Document chính
            if main_doc.file:
                file_version = DocumentFileVersion.objects.create(
                    document=main_doc,
                    file=main_doc.file,
                    file_name=main_doc.file.name.split('/')[-1] if main_doc.file.name else 'unknown',
                    file_size=main_doc.file_size or 0,
                    file_type=main_doc.file_type or '',
                    uploaded_by=main_doc.created_by,
                    is_current=True,
                    change_note='File gốc',
                    version_number=1
                )
                self.stdout.write(f'Created file version v1 for main document: {main_doc.title}')
            
            # Tạo DocumentFileVersion cho các Document còn lại (như các version)
            version_number = 2
            for doc in docs[1:]:
                if doc.file:
                    file_version = DocumentFileVersion.objects.create(
                        document=main_doc,  # Gắn vào Document chính
                        file=doc.file,
                        file_name=doc.file.name.split('/')[-1] if doc.file.name else 'unknown',
                        file_size=doc.file_size or 0,
                        file_type=doc.file_type or '',
                        uploaded_by=doc.created_by,
                        is_current=False,  # Không phải file hiện tại
                        change_note=f'Version từ Document ID {doc.id}',
                        version_number=version_number
                    )
                    self.stdout.write(f'Created file version v{version_number} for {main_doc.title}')
                    version_number += 1
                
                # Xóa Document trùng lặp
                doc.delete()
                self.stdout.write(f'Deleted duplicate document ID {doc.id}')
        
        # Xử lý các Document không trùng lặp
        remaining_docs = Document.objects.all()
        for doc in remaining_docs:
            if doc.file and not DocumentFileVersion.objects.filter(document=doc).exists():
                file_version = DocumentFileVersion.objects.create(
                    document=doc,
                    file=doc.file,
                    file_name=doc.file.name.split('/')[-1] if doc.file.name else 'unknown',
                    file_size=doc.file_size or 0,
                    file_type=doc.file_type or '',
                    uploaded_by=doc.created_by,
                    is_current=True,
                    change_note='File gốc',
                    version_number=1
                )
                self.stdout.write(f'Created file version v1 for {doc.title}')
        
        self.stdout.write(self.style.SUCCESS('Migration completed!')) 