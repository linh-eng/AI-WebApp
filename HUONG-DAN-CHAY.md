# Hướng dẫn chạy thử (dành cho người không rành kỹ thuật)

Ứng dụng chạy trên máy tính của chị, mở bằng trình duyệt (Chrome/Edge). Chỉ cần
cài **một lần**, các lần sau bấm chạy là dùng ngay.

Có 2 cách. **Cách A** dễ nhất nếu máy đã có Python.

---

## Cách A — Dùng Python (khuyên dùng)

### Bước 1: Cài Python (chỉ làm 1 lần)
- Tải tại: https://www.python.org/downloads/
- **Windows:** khi cài, nhớ TÍCH vào ô **"Add Python to PATH"** ở màn hình đầu.
- macOS: tải bản mới nhất và cài như ứng dụng bình thường.

### Bước 2: Tải mã nguồn về máy
- Vào trang GitHub của dự án → nhánh `claude/webapp-business-report-excel-pkgwsr`
  → bấm nút xanh **Code** → **Download ZIP** → giải nén ra một thư mục.
  (Hoặc nhờ bạn IT `git clone` giúp.)

### Bước 3: Chạy
- **Windows:** vào thư mục vừa giải nén, **bấm đúp** vào file **`run.bat`**.
- **macOS:** mở **Terminal**, kéo–thả file `run.sh` vào rồi Enter (hoặc gõ
  `cd` tới thư mục rồi chạy `./run.sh`).

Lần đầu sẽ tự cài thư viện (khoảng 1–2 phút). Sau đó trình duyệt tự mở trang
đăng nhập.

### Bước 4: Đăng nhập
- Địa chỉ: **http://127.0.0.1:8000**
- Tài khoản: **admin** — Mật khẩu: **admin123**

### Tắt ứng dụng
- Đóng cửa sổ đen (Command Prompt/Terminal) hoặc bấm **Ctrl + C** trong đó.

---

## Cách B — Dùng Docker (nếu máy/máy chủ đã có Docker)

Mở Terminal/PowerShell tại thư mục dự án và gõ:

```bash
docker compose up -d --build
```

Rồi mở trình duyệt vào `http://127.0.0.1:8000` (hoặc `http://<địa-chỉ-máy-chủ>:8000`
nếu chạy trên máy chủ để cả phòng dùng chung).

Tắt: `docker compose down`.

---

## Câu hỏi thường gặp

**Cả phòng dùng chung được không?**
Được. Cài trên một máy chủ nội bộ (hoặc một máy để bật thường xuyên), chạy với
địa chỉ `0.0.0.0` — mọi người trong mạng công ty vào `http://<IP-máy-đó>:8000`.
Em có thể hướng dẫn thêm khi chị cần.

**Dữ liệu lưu ở đâu?**
Trong thư mục `data/` (file SQLite). Nên sao lưu thư mục này định kỳ.

**Đổi mật khẩu admin?**
Đặt biến môi trường `ADMIN_PASSWORD` trước khi chạy, hoặc báo em thêm màn hình
quản lý tài khoản ở giai đoạn sau.

**Bị lỗi khi chạy?**
Chụp màn hình cửa sổ đen báo lỗi gửi em, em xử lý ngay.
