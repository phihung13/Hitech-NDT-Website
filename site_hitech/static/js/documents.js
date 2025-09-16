// Documents functionality
$(document).ready(function() {
    // Auto submit search form on input
    let searchTimeout;
    $('.search-input').on('input', function() {
        clearTimeout(searchTimeout);
        const form = $(this).closest('form');
        searchTimeout = setTimeout(function() {
            form.submit();
        }, 500);
    });
    
    // Smooth scroll to top when filters change
    $('.category-filter').on('click', function() {
        $('html, body').animate({
            scrollTop: 0
        }, 300);
    });
    
    // Show loading state for downloads
    $('a[download]').on('click', function() {
        const btn = $(this);
        const originalText = btn.html();
        btn.html('<i class="fas fa-spinner fa-spin me-1"></i>Đang tải...');
        btn.prop('disabled', true);
        
        setTimeout(function() {
            btn.html(originalText);
            btn.prop('disabled', false);
        }, 2000);
    });
    
    // Tooltips for access level badges
    $('[data-bs-toggle="tooltip"]').tooltip();
});

// Show version history
function showVersionHistory(documentId) {
    fetch(`/api/documents/${documentId}/versions/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                let html = '<div class="version-list">';
                data.versions.forEach(version => {
                    html += `
                        <div class="version-item ${version.is_latest ? 'latest' : ''}">
                            <div class="version-info">
                                <span class="version-number">v${version.version}</span>
                                <span class="version-date">${version.updated_at}</span>
                                <span class="version-user">${version.created_by}</span>
                                <span class="version-size">${version.file_size}</span>
                            </div>
                            <div class="version-actions">
                                <a href="${version.file_url}" class="btn btn-sm btn-outline-primary" target="_blank">
                                    <i class="fas fa-download"></i> Tải
                                </a>
                                ${!version.is_latest ? `
                                    <button class="btn btn-sm btn-outline-warning" onclick="restoreVersion(${version.id})">
                                        <i class="fas fa-undo"></i> Khôi phục
                                    </button>
                                ` : ''}
                            </div>
                        </div>
                    `;
                });
                html += '</div>';
                
                document.getElementById('versionHistoryContent').innerHTML = html;
                const modal = new bootstrap.Modal(document.getElementById('versionHistoryModal'));
                modal.show();
            } else {
                alert('Lỗi khi tải lịch sử phiên bản: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Lỗi khi tải lịch sử phiên bản');
        });
}

// Update document
function updateDocument(documentId) {
    console.log("=== DEBUG: updateDocument called with ID:", documentId);
    document.getElementById('parentDocumentId').value = documentId;
    
    // Set form action to the dedicated update view
    const form = document.getElementById('updateDocumentForm');
    form.action = `/documents/update/${documentId}/`; // POST-only endpoint
    
    console.log("=== DEBUG: Form action set to:", form.action);
    const modal = new bootstrap.Modal(document.getElementById('updateDocumentModal'));
    modal.show();
}

// Delete document
function deleteDocument(documentId) {
    if (confirm('Bạn có chắc muốn xóa tài liệu này và tất cả phiên bản?')) {
        fetch(`/api/documents/${documentId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Lỗi xóa tài liệu: ' + data.error);
            }
        });
    }
}

// Restore version
function restoreVersion(versionId) {
    if (confirm('Bạn có chắc muốn khôi phục phiên bản này?')) {
        fetch(`/api/documents/${versionId}/restore/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Lỗi khôi phục phiên bản: ' + data.error);
            }
        });
    }
}

// Copy share link
function copyShareLink(url) {
    navigator.clipboard.writeText(url).then(function() {
        if (window.toastr) {
            toastr.success('Đã sao chép link chia sẻ');
        } else {
            alert('Đã sao chép link: ' + url);
        }
    }, function() {
        alert('Không thể sao chép link. Vui lòng thử lại.');
    });
} 