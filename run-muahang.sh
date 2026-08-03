#!/usr/bin/env bash
# ===== Chạy WebApp Báo cáo MUA HÀNG THNG trên macOS / Linux (cổng 8010) =====
# Dùng cổng 8010 để chạy SONG SONG với app khác đang ở cổng 8000.
# Chạy: mở Terminal tại thư mục này rồi gõ:  ./run-muahang.sh
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
echo "  WebApp MUA HÀNG — Mở trình duyệt vào:  http://127.0.0.1:8010"
echo "  Đăng nhập:  admin  /  admin123"
echo "  Để TẮT ứng dụng: bấm Ctrl + C"
echo "================================================================"
echo

# Tự mở trình duyệt sau 3 giây
( sleep 3; (open http://127.0.0.1:8010 2>/dev/null || xdg-open http://127.0.0.1:8010 2>/dev/null) ) &

python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
