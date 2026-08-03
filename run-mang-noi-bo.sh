#!/usr/bin/env bash
# ===== Chạy WebApp MUA HÀNG cho CẢ PHÒNG truy cập qua mạng nội bộ (LAN) - macOS/Linux =====
# Chạy trên MỘT máy làm "máy chủ". Đồng nghiệp mở http://<IP-máy-này>:8010
# Dùng cổng 8010 để chạy song song với app khác (vd Kinh Doanh ở cổng 8000).
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "Đang tạo môi trường lần đầu..."
  python3 -m venv .venv
fi
source .venv/bin/activate
echo "Đang cài đặt / kiểm tra thư viện..."
python -m pip install --disable-pip-version-check -q -r requirements.txt

echo
echo "=========================================================="
echo "  WebApp MUA HÀNG — ĐỊA CHỈ ĐỂ ĐỒNG NGHIỆP TRUY CẬP"
echo "  (chọn dòng inet 192.168... / 10...):"
ip -4 addr show 2>/dev/null | grep inet | grep -v 127.0.0.1 || ifconfig 2>/dev/null | grep "inet " | grep -v 127.0.0.1
echo
echo "  Đồng nghiệp mở trình duyệt:  http://<IP-máy-này>:8010"
echo "  Trên chính máy này:          http://127.0.0.1:8010"
echo "  Đăng nhập admin / admin123 (đổi mật khẩu ngay)"
echo "  Giữ máy bật để mọi người dùng được. Tắt: bấm Ctrl + C."
echo "=========================================================="
echo

python -m uvicorn app.main:app --host 0.0.0.0 --port 8010
