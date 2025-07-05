#!/bin/bash

# ========================================
# HITECH NDT - GIT SETUP SCRIPT
# Script setup Git credentials cho private repo
# ========================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

setup_ssh_key() {
    print_status "========================================="
    print_status "SETUP SSH KEY CHO GITHUB"
    print_status "========================================="
    echo
    
    SSH_DIR="/root/.ssh"
    SSH_KEY="$SSH_DIR/id_rsa_github"
    
    # Create .ssh directory if not exists
    mkdir -p $SSH_DIR
    chmod 700 $SSH_DIR
    
    if [ -f "$SSH_KEY" ]; then
        print_warning "SSH key đã tồn tại tại: $SSH_KEY"
        echo -n "Tạo key mới? (y/N): "
        read -r RECREATE
        if [[ ! $RECREATE =~ ^[Yy]$ ]]; then
            print_status "Sử dụng SSH key hiện có"
            cat "$SSH_KEY.pub"
            return 0
        fi
    fi
    
    print_status "Tạo SSH key mới..."
    
    echo -n "Nhập email GitHub của bạn: "
    read -r EMAIL
    
    # Generate SSH key
    ssh-keygen -t rsa -b 4096 -C "$EMAIL" -f "$SSH_KEY" -N ""
    
    # Set permissions
    chmod 600 "$SSH_KEY"
    chmod 644 "$SSH_KEY.pub"
    
    # Add to SSH agent
    eval "$(ssh-agent -s)"
    ssh-add "$SSH_KEY"
    
    # Create SSH config
    cat > "$SSH_DIR/config" << EOF
Host github.com
    HostName github.com
    User git
    IdentityFile $SSH_KEY
    IdentitiesOnly yes
EOF
    
    chmod 600 "$SSH_DIR/config"
    
    print_success "SSH key đã được tạo!"
    echo
    print_warning "========================================="
    print_warning "QUAN TRỌNG: COPY PUBLIC KEY SAU ĐÂY"
    print_warning "========================================="
    echo
    cat "$SSH_KEY.pub"
    echo
    print_status "1. Copy đoạn text trên"
    print_status "2. Vào GitHub.com > Settings > SSH and GPG keys"
    print_status "3. Click 'New SSH key'"
    print_status "4. Paste key và save"
    echo
    echo -n "Đã thêm key vào GitHub? (y/N): "
    read -r ADDED
    
    if [[ $ADDED =~ ^[Yy]$ ]]; then
        test_ssh_connection
    else
        print_warning "Hãy thêm key vào GitHub trước khi tiếp tục!"
    fi
}

setup_personal_access_token() {
    print_status "========================================="
    print_status "SETUP PERSONAL ACCESS TOKEN"
    print_status "========================================="
    echo
    
    print_status "Hướng dẫn tạo Personal Access Token:"
    print_status "1. Vào GitHub.com > Settings > Developer settings"
    print_status "2. Personal access tokens > Tokens (classic)"
    print_status "3. Generate new token (classic)"
    print_status "4. Chọn scope: repo (full control)"
    print_status "5. Copy token được tạo"
    echo
    
    echo -n "Nhập GitHub username: "
    read -r USERNAME
    echo -n "Nhập Personal Access Token: "
    read -s TOKEN
    echo
    
    # Configure git credentials
    git config --global credential.helper store
    
    # Create credentials file
    cat > /root/.git-credentials << EOF
https://$USERNAME:$TOKEN@github.com
EOF
    
    chmod 600 /root/.git-credentials
    
    print_success "Personal Access Token đã được cấu hình!"
    
    test_git_access "$USERNAME"
}

test_ssh_connection() {
    print_status "Test kết nối SSH..."
    
    if ssh -T git@github.com -o StrictHostKeyChecking=no 2>&1 | grep -q "successfully authenticated"; then
        print_success "✓ SSH connection thành công!"
        return 0
    else
        print_error "✗ SSH connection thất bại"
        print_status "Kiểm tra lại SSH key trên GitHub"
        return 1
    fi
}

test_git_access() {
    local USERNAME="$1"
    print_status "Test Git access..."
    
    if git ls-remote "https://github.com/$USERNAME/Hitech-NDT-Website.git" >/dev/null 2>&1; then
        print_success "✓ Git access thành công!"
        return 0
    else
        print_error "✗ Git access thất bại"
        print_status "Kiểm tra lại token và repository name"
        return 1
    fi
}

main() {
    print_status "========================================="
    print_status "HITECH NDT - GIT SETUP"
    print_status "========================================="
    echo
    
    check_root
    
    print_status "Chọn phương thức authentication:"
    print_status "1) SSH Key (Khuyến nghị)"
    print_status "2) Personal Access Token"
    echo -n "Lựa chọn (1/2): "
    read -r CHOICE
    
    case $CHOICE in
        1)
            setup_ssh_key
            ;;
        2)
            setup_personal_access_token
            ;;
        *)
            print_error "Lựa chọn không hợp lệ!"
            exit 1
            ;;
    esac
    
    echo
    print_success "========================================="
    print_success "GIT SETUP HOÀN THÀNH!"
    print_success "========================================="
    print_status "Bây giờ có thể chạy: sudo bash deploy.sh"
    print_status "Hoặc: sudo bash update.sh"
}

# Run main function
main "$@" 