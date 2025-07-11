#!/bin/bash

# ========================================
# HITECH NDT - UPDATE SCRIPT
# Script cập nhật code mới nhất
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
GITHUB_REPO="https://github.com/phihung13/Hitech-NDT-Website.git"
BRANCH="main"

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

backup_current() {
    print_status "Backup version hiện tại..."
    
    if [ -d "$PROJECT_DIR" ]; then
        cp -r $PROJECT_DIR $PROJECT_DIR.backup.$(date +%Y%m%d_%H%M%S)
        print_success "Backup hoàn thành"
    else
        print_error "Thư mục project không tồn tại: $PROJECT_DIR"
        exit 1
    fi
}

check_git_access() {
    print_status "Kiểm tra Git access..."
    
    # Check if git credentials are configured
    if [ ! -f "/root/.git-credentials" ] && [ ! -f "/root/.ssh/config" ]; then
        print_error "Git credentials chưa được cấu hình!"
        print_status "Chạy: sudo bash setup_git.sh"
        exit 1
    fi
    
    # Test access to repository
    if ! git ls-remote $GITHUB_REPO >/dev/null 2>&1; then
        print_error "Không thể truy cập repository: $GITHUB_REPO"
        print_status "Kiểm tra lại Git credentials hoặc chạy: sudo bash setup_git.sh"
        exit 1
    fi
    
    print_success "✓ Git access OK"
}

update_code() {
    print_status "Cập nhật code mới nhất..."
    
    # Check Git access first
    check_git_access
    
    cd $PROJECT_DIR
    
    # Check if this is a Git repository
    if [ -d ".git" ]; then
        print_status "Pull từ Git repository..."
        
        # Backup production settings
        cp site_hitech/site_hitech/settings_production.py /tmp/settings_production_backup.py 2>/dev/null
        
        # Stash any local changes
        git stash push -m "Auto-stash before update $(date)"
        
        # Pull latest changes
        if git pull origin $BRANCH; then
            print_success "✓ Git pull thành công"
            
            # Restore production settings if backup exists
            if [ -f "/tmp/settings_production_backup.py" ]; then
                cp /tmp/settings_production_backup.py site_hitech/site_hitech/settings_production.py
                print_status "✓ Production settings đã được khôi phục"
            fi
        else
            print_error "✗ Git pull thất bại"
            exit 1
        fi
    else
        print_warning "Không phải Git repository, re-clone từ Git..."
        
        # Backup important files
        cp site_hitech/site_hitech/settings_production.py /tmp/settings_production_backup.py 2>/dev/null
        cp -r media /tmp/media_backup 2>/dev/null
        
        # Remove current code and re-clone
        cd /var/www
        rm -rf $PROJECT_DIR
        
        if git clone -b $BRANCH $GITHUB_REPO $PROJECT_NAME; then
            print_success "✓ Git clone thành công"
            
            cd $PROJECT_DIR
            
            # Restore important files
            if [ -f "/tmp/settings_production_backup.py" ]; then
                cp /tmp/settings_production_backup.py site_hitech/site_hitech/settings_production.py
                print_status "✓ Production settings đã được khôi phục"
            fi
            
            if [ -d "/tmp/media_backup" ]; then
                cp -r /tmp/media_backup/* media/ 2>/dev/null
                print_status "✓ Media files đã được khôi phục"
            fi
        else
            print_error "Git clone thất bại!"
            exit 1
        fi
    fi
    
    print_success "Code đã được cập nhật"
}

update_dependencies() {
    print_status "Cập nhật dependencies..."
    
    cd $PROJECT_DIR/site_hitech
    source ../venv/bin/activate
    
    pip install --upgrade pip
    pip install -r requirements.txt --upgrade
    
    print_success "Dependencies đã được cập nhật"
}

run_migrations() {
    print_status "Chạy database migrations..."
    
    cd $PROJECT_DIR/site_hitech
    source ../venv/bin/activate
    export DJANGO_SETTINGS_MODULE=site_hitech.settings_production
    
    python manage.py migrate
    python manage.py collectstatic --noinput
    
    # Run setup scripts if they exist
    [ -f "create_homepage_settings.py" ] && python create_homepage_settings.py 2>/dev/null
    [ -f "setup_seo_and_about_data.py" ] && python setup_seo_and_about_data.py 2>/dev/null
    
    print_success "Migrations hoàn thành"
}

restart_services() {
    print_status "Restart services..."
    
    # Stop services
    systemctl stop $SERVICE_NAME
    systemctl stop nginx
    
    # Set permissions
    chown -R www-data:www-data $PROJECT_DIR
    chmod -R 755 $PROJECT_DIR
    
    # Start services
    systemctl start $SERVICE_NAME
    systemctl start nginx
    
    # Check status
    sleep 3
    
    if systemctl is-active --quiet $SERVICE_NAME; then
        print_success "✓ Django service đang chạy"
    else
        print_error "✗ Django service lỗi"
        print_status "Checking logs..."
        journalctl -u $SERVICE_NAME --no-pager -n 10
    fi
    
    if systemctl is-active --quiet nginx; then
        print_success "✓ Nginx đang chạy"
    else
        print_error "✗ Nginx lỗi"
    fi
    
    print_success "Services đã được restart"
}

test_website() {
    print_status "Kiểm tra website..."
    
    sleep 2
    
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost)
    
    if [[ "$HTTP_STATUS" =~ ^(200|301|302)$ ]]; then
        print_success "✓ Website hoạt động bình thường (HTTP $HTTP_STATUS)"
    else
        print_error "✗ Website có vấn đề (HTTP $HTTP_STATUS)"
        
        # Try to rollback if there's a recent backup
        LATEST_BACKUP=$(ls -t $PROJECT_DIR.backup.* 2>/dev/null | head -1)
        if [ -n "$LATEST_BACKUP" ]; then
            print_status "Rolling back to latest backup..."
            systemctl stop $SERVICE_NAME
            rm -rf $PROJECT_DIR
            mv "$LATEST_BACKUP" $PROJECT_DIR
            restart_services
        fi
    fi
}

cleanup_old_backups() {
    print_status "Dọn dẹp backup cũ..."
    
    # Keep only 5 most recent backups
    ls -t $PROJECT_DIR.backup.* 2>/dev/null | tail -n +6 | xargs rm -rf 2>/dev/null
    
    print_success "Cleanup hoàn thành"
}

main() {
    print_status "========================================="
    print_status "HITECH NDT - UPDATE CODE"
    print_status "========================================="
    echo
    
    check_root
    backup_current
    update_code
    update_dependencies
    run_migrations
    restart_services
    test_website
    cleanup_old_backups
    
    echo
    print_success "========================================="
    print_success "UPDATE HOÀN THÀNH!"
    print_success "========================================="
    print_status "Website: https://hitechndt.vn"
    print_status "Để xem logs: sudo journalctl -u $SERVICE_NAME -f"
    print_status "Để rollback: sudo bash rollback.sh"
    echo
}

# Run main function
main "$@"