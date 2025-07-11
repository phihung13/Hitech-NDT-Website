#!/bin/bash

# =============================================================================
# HITECH NDT WEBSITE - GIT SETUP SCRIPT
# =============================================================================
# Script này sẽ cấu hình Git access cho deployment
# Author: Hitech NDT Team
# Version: 1.0
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Hitech NDT"
GITHUB_REPO="https://github.com/phihung13/Hitech-NDT-Website.git"
GIT_USER="hitech-ndt-deploy"
GIT_EMAIL="deploy@hitechndt.vn"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# =============================================================================
# GIT SETUP FUNCTIONS
# =============================================================================

install_git() {
    log_info "Installing Git..."
    
    # Update package list
    apt update
    
    # Install Git
    apt install -y git
    
    # Verify installation
    if command -v git &> /dev/null; then
        local git_version=$(git --version)
        log_success "Git installed: $git_version"
    else
        log_error "Failed to install Git"
        exit 1
    fi
}

configure_git() {
    log_info "Configuring Git..."
    
    # Set global Git configuration
    git config --global user.name "$GIT_USER"
    git config --global user.email "$GIT_EMAIL"
    git config --global init.defaultBranch main
    git config --global pull.rebase false
    
    # Set safe directory (for security)
    git config --global --add safe.directory '*'
    
    log_success "Git configured with user: $GIT_USER <$GIT_EMAIL>"
}

setup_ssh_key() {
    log_info "Setting up SSH key for Git access..."
    
    local ssh_dir="/root/.ssh"
    local ssh_key="$ssh_dir/id_rsa"
    local ssh_pub="$ssh_key.pub"
    
    # Create SSH directory if it doesn't exist
    mkdir -p "$ssh_dir"
    chmod 700 "$ssh_dir"
    
    # Generate SSH key if it doesn't exist
    if [ ! -f "$ssh_key" ]; then
        log_info "Generating SSH key..."
        ssh-keygen -t rsa -b 4096 -C "$GIT_EMAIL" -f "$ssh_key" -N ""
        chmod 600 "$ssh_key"
        chmod 644 "$ssh_pub"
        log_success "SSH key generated"
    else
        log_info "SSH key already exists"
    fi
    
    # Add GitHub to known hosts
    if ! grep -q "github.com" "$ssh_dir/known_hosts" 2>/dev/null; then
        log_info "Adding GitHub to known hosts..."
        ssh-keyscan -H github.com >> "$ssh_dir/known_hosts"
        log_success "GitHub added to known hosts"
    fi
    
    # Display public key
    echo
    log_warning "=== SSH PUBLIC KEY ==="
    log_warning "Copy this key and add it to your GitHub repository:"
    log_warning "GitHub → Settings → Deploy keys → Add deploy key"
    echo
    cat "$ssh_pub"
    echo
    log_warning "========================"
    echo
}

test_git_access() {
    log_info "Testing Git access..."
    
    # Test SSH connection to GitHub
    if ssh -T git@github.com -o StrictHostKeyChecking=no 2>&1 | grep -q "successfully authenticated"; then
        log_success "SSH connection to GitHub successful"
    else
        log_warning "SSH connection test inconclusive (this is normal if using HTTPS)"
    fi
    
    # Test repository access
    local temp_dir="/tmp/git_test_$(date +%s)"
    
    log_info "Testing repository clone..."
    if git clone --depth 1 "$GITHUB_REPO" "$temp_dir" &>/dev/null; then
        log_success "Repository clone successful"
        rm -rf "$temp_dir"
    else
        log_warning "Repository clone failed with SSH, trying HTTPS..."
        if git clone --depth 1 "$GITHUB_REPO" "$temp_dir" &>/dev/null; then
            log_success "Repository clone successful with HTTPS"
            rm -rf "$temp_dir"
        else
            log_error "Repository clone failed"
            log_error "Please check:"
            log_error "1. Repository URL is correct"
            log_error "2. SSH key is added to GitHub (if using SSH)"
            log_error "3. Repository is public or you have access"
            return 1
        fi
    fi
}

setup_git_credentials() {
    log_info "Setting up Git credentials..."
    
    # Configure credential helper for HTTPS
    git config --global credential.helper store
    
    # Create credentials file with proper permissions
    local cred_file="/root/.git-credentials"
    touch "$cred_file"
    chmod 600 "$cred_file"
    
    log_info "Git credentials helper configured"
    log_warning "If using HTTPS, you may need to enter credentials on first clone"
}

optimize_git_config() {
    log_info "Optimizing Git configuration..."
    
    # Performance optimizations
    git config --global core.preloadindex true
    git config --global core.fscache true
    git config --global gc.auto 256
    
    # Security settings
    git config --global transfer.fsckobjects true
    git config --global fetch.fsckobjects true
    git config --global receive.fsckObjects true
    
    # Useful aliases
    git config --global alias.st status
    git config --global alias.co checkout
    git config --global alias.br branch
    git config --global alias.ci commit
    git config --global alias.unstage 'reset HEAD --'
    git config --global alias.last 'log -1 HEAD'
    git config --global alias.visual '!gitk'
    
    log_success "Git configuration optimized"
}

show_git_info() {
    echo
    log_info "=== GIT CONFIGURATION SUMMARY ==="
    echo
    log_info "Git Version: $(git --version)"
    log_info "User Name: $(git config --global user.name)"
    log_info "User Email: $(git config --global user.email)"
    log_info "Default Branch: $(git config --global init.defaultBranch)"
    echo
    
    if [ -f "/root/.ssh/id_rsa.pub" ]; then
        log_info "SSH Key: Available"
        log_info "SSH Key Path: /root/.ssh/id_rsa"
    else
        log_warning "SSH Key: Not found"
    fi
    
    echo
    log_info "Repository: $GITHUB_REPO"
    echo
    log_success "Git setup completed!"
    echo
}

# =============================================================================
# MAIN FUNCTION
# =============================================================================

main() {
    echo "==============================================="
    echo "🔧 $PROJECT_NAME - GIT SETUP SCRIPT"
    echo "==============================================="
    echo
    
    # Check if running as root
    check_root
    
    # Install and configure Git
    install_git
    configure_git
    setup_git_credentials
    optimize_git_config
    
    # Setup SSH (optional but recommended)
    echo
    read -p "Do you want to setup SSH key for Git? (recommended) (y/N): " setup_ssh
    if [[ "$setup_ssh" =~ ^[Yy]$ ]]; then
        setup_ssh_key
        
        echo
        read -p "Have you added the SSH key to GitHub? (y/N): " key_added
        if [[ "$key_added" =~ ^[Yy]$ ]]; then
            test_git_access
        else
            log_warning "Please add the SSH key to GitHub before running deploy.sh"
        fi
    else
        log_info "Skipping SSH setup, will use HTTPS"
        test_git_access
    fi
    
    # Show summary
    show_git_info
    
    echo "==============================================="
    log_success "🎉 GIT SETUP COMPLETED!"
    echo "==============================================="
    echo
    log_info "Next steps:"
    log_info "1. If using SSH: Add the public key to GitHub"
    log_info "2. Run: sudo bash deploy.sh"
    echo
}

# Run main function
main "$@"