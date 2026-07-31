#!/usr/bin/env bash
# ===== Chạy WebApp Báo cáo Kinh doanh THNG trên macOS / Linux =====
# Chạy: mở Terminal tại thư mục này rồi gõ:  ./run.sh
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
echo "================================================================"
echo "  Mở trình duyệt vào địa chỉ:  http://127.0.0.1:8000"
echo "  Đăng nhập:  admin  /  admin123"
echo "  Để TẮT ứng dụng: bấm Ctrl + C"
echo "================================================================"
echo

# Tự mở trình duyệt sau 3 giây
( sleep 3; (open http://127.0.0.1:8000 2>/dev/null || xdg-open http://127.0.0.1:8000 2>/dev/null) ) &

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
