#!/bin/bash

# ========================================
# HITECH NDT - ROLLBACK SCRIPT
# Script rollback về version trước đó
# ========================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_NAME="hitech_ndt"
PROJECT_DIR="/var/www/$PROJECT_NAME"
SERVICE_NAME="hitech-ndt"

# Functions
print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "Script cần chạy với quyền root: sudo $0"
        exit 1
    fi
}

list_backups() {
    print_status "Available backups:"
    echo
    
    BACKUPS=($(ls -t $PROJECT_DIR.backup.* 2>/dev/null))
    
    if [ ${#BACKUPS[@]} -eq 0 ]; then
        print_error "Không tìm thấy backup nào!"
        exit 1
    fi
    
    for i in "${!BACKUPS[@]}"; do
        BACKUP_DATE=$(echo "${BACKUPS[$i]}" | sed 's/.*\.backup\.//')
        FORMATTED_DATE=$(date -d "${BACKUP_DATE:0:8} ${BACKUP_DATE:9:2}:${BACKUP_DATE:11:2}" "+%d/%m/%Y %H:%M" 2>/dev/null || echo "$BACKUP_DATE")
        printf "%2d) %s (%s)\n" $((i+1)) "$(basename "${BACKUPS[$i]}")" "$FORMATTED_DATE"
    done
    echo
}

select_backup() {
    list_backups
    
    BACKUPS=($(ls -t $PROJECT_DIR.backup.* 2>/dev/null))
    
    echo -n "Chọn backup để rollback (1-${#BACKUPS[@]}) hoặc 'q' để thoát: "
    read -r CHOICE
    
    if [[ "$CHOICE" = "q" || "$CHOICE" = "Q" ]]; then
        print_status "Rollback đã hủy"
        exit 0
    fi
    
    if ! [[ "$CHOICE" =~ ^[0-9]+$ ]] || [ "$CHOICE" -lt 1 ] || [ "$CHOICE" -gt ${#BACKUPS[@]} ]; then
        print_error "Lựa chọn không hợp lệ!"
        exit 1
    fi
    
    SELECTED_BACKUP="${BACKUPS[$((CHOICE-1))]}"
    BACKUP_DATE=$(echo "$SELECTED_BACKUP" | sed 's/.*\.backup\.//')
    FORMATTED_DATE=$(date -d "${BACKUP_DATE:0:8} ${BACKUP_DATE:9:2}:${BACKUP_DATE:11:2}" "+%d/%m/%Y %H:%M" 2>/dev/null || echo "$BACKUP_DATE")
    
    echo
    print_warning "⚠️  Bạn sắp rollback về version: $FORMATTED_DATE"
    print_warning "⚠️  Website sẽ tạm dừng trong vài phút"
    echo -n "Tiếp tục? (y/N): "
    read -r CONFIRM
    
    if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
        print_status "Rollback đã hủy"
        exit 0
    fi
    
    echo "$SELECTED_BACKUP"
}

perform_rollback() {
    local BACKUP_PATH="$1"
    
    print_status "Bắt đầu rollback..."
    
    # Stop services
    print_status "Dừng services..."
    systemctl stop $SERVICE_NAME
    systemctl stop nginx
    
    # Backup current version before rollback
    if [ -d "$PROJECT_DIR" ]; then
        print_status "Backup version hiện tại trước khi rollback..."
        mv $PROJECT_DIR $PROJECT_DIR.before_rollback.$(date +%Y%m%d_%H%M%S)
    fi
    
    # Restore from backup
    print_status "Khôi phục từ backup..."
    cp -r "$BACKUP_PATH" "$PROJECT_DIR"
    
    # Set permissions
    print_status "Thiết lập permissions..."
    chown -R www-data:www-data $PROJECT_DIR
    chmod -R 755 $PROJECT_DIR
    
    # Start services
    print_status "Khởi động services..."
    systemctl start $SERVICE_NAME
    systemctl start nginx
    
    print_success "Rollback hoàn thành"
}

test_rollback() {
    print_status "Kiểm tra website sau rollback..."
    
    sleep 3
    
    # Check services
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_success "✓ Django service đang chạy"
    else
        print_error "✗ Django service lỗi"
        journalctl -u $SERVICE_NAME --no-pager -n 10
        return 1
    fi
    
    if systemctl is-active --quiet nginx; then
        print_success "✓ Nginx đang chạy"
    else
        print_error "✗ Nginx lỗi"
        return 1
    fi
    
    # Check website
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost)
    
    if [[ "$HTTP_STATUS" =~ ^(200|301|302)$ ]]; then
        print_success "✓ Website hoạt động bình thường (HTTP $HTTP_STATUS)"
        return 0
    else
        print_error "✗ Website có vấn đề (HTTP $HTTP_STATUS)"
        return 1
    fi
}

cleanup_rollback_backup() {
    print_status "Dọn dẹp..."
    
    # Remove the rollback backup if successful
    rm -rf $PROJECT_DIR.before_rollback.* 2>/dev/null
    
    print_success "Cleanup hoàn thành"
}

main() {
    print_status "========================================="
    print_status "HITECH NDT - ROLLBACK"
    print_status "========================================="
    echo
    
    check_root
    
    BACKUP_TO_RESTORE=$(select_backup)
    
    if [ -n "$BACKUP_TO_RESTORE" ]; then
        perform_rollback "$BACKUP_TO_RESTORE"
        
        if test_rollback; then
            cleanup_rollback_backup
            
            echo
            print_success "========================================="
            print_success "ROLLBACK THÀNH CÔNG!"
            print_success "========================================="
            print_success "Website: https://hitechndt.vn"
            echo
            print_status "Để xem logs: sudo journalctl -u $SERVICE_NAME -f"
            print_status "Để update lại: sudo bash update.sh"
        else
            echo
            print_error "========================================="
            print_error "ROLLBACK CÓ VẤN ĐỀ!"
            print_error "========================================="
            print_status "Kiểm tra logs: sudo journalctl -u $SERVICE_NAME -f"
            
            # Try to restore pre-rollback state
            RESTORE_BACKUP=$(ls -t $PROJECT_DIR.before_rollback.* 2>/dev/null | head -1)
            if [ -n "$RESTORE_BACKUP" ]; then
                print_status "Có thể khôi phục version trước rollback với:"
                print_status "sudo mv \"$RESTORE_BACKUP\" \"$PROJECT_DIR\""
                print_status "sudo systemctl restart $SERVICE_NAME nginx"
            fi
        fi
    fi
}

# Run main function
main "$@" 