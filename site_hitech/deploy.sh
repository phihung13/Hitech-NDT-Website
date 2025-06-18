#!/bin/bash
# Script triển khai Hitech-NDT-Website lên hosting

# Hiển thị thông báo màu
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

echo -e "${GREEN}Bắt đầu quá trình triển khai Hitech-NDT-Website...${NC}"

# 1. Cập nhật mã nguồn từ git (nếu cần)
if [ -d ".git" ]; then
    echo -e "${YELLOW}Cập nhật mã nguồn từ git...${NC}"
    git pull
fi

# 2. Cài đặt hoặc cập nhật các thư viện cần thiết
echo -e "${YELLOW}Cài đặt/cập nhật các thư viện cần thiết...${NC}"
pip install -r ../requirements.txt

# 3. Áp dụng migrations
echo -e "${YELLOW}Áp dụng migrations...${NC}"
python manage.py migrate

# 4. Thu thập static files
echo -e "${YELLOW}Thu thập static files...${NC}"
python manage.py collectstatic --noinput

# 5. Kiểm tra cấu hình
echo -e "${YELLOW}Kiểm tra cấu hình...${NC}"
python manage.py check --deploy

# 6. Khởi động lại ứng dụng (nếu đang chạy trên VPS với supervisor)
if command -v supervisorctl &> /dev/null; then
    echo -e "${YELLOW}Khởi động lại ứng dụng với Supervisor...${NC}"
    sudo supervisorctl restart hitech-ndt:*
fi

# 7. Khởi động lại Nginx (nếu đang chạy trên VPS với nginx)
if command -v nginx &> /dev/null; then
    echo -e "${YELLOW}Khởi động lại Nginx...${NC}"
    sudo systemctl restart nginx
fi

echo -e "${GREEN}Quá trình triển khai hoàn tất!${NC}"