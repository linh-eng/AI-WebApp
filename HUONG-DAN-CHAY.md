# Hướng dẫn chạy WebApp MUA HÀNG (dành cho người không rành kỹ thuật)

Ứng dụng chạy trên một máy tính, mở bằng trình duyệt (Chrome/Edge). Chỉ cần cài
**một lần**, các lần sau bấm chạy là dùng ngay.

> App này chạy ở **cổng 8010** (để chạy song song với app Kinh Doanh ở cổng 8000).

---

## Bước 1: Cài Python (chỉ làm 1 lần)

- Tải tại: https://www.python.org/downloads/
- **Windows:** khi cài, ở màn hình đầu **NHỚ TÍCH ô "Add Python to PATH"** rồi mới
  bấm *Install Now*. (Bỏ qua bước tích ô này là nguyên nhân lỗi thường gặp nhất.)
- macOS: tải bản mới nhất và cài như ứng dụng bình thường.

## Bước 2: Tải mã nguồn về máy

- Mở: https://github.com/linh-eng/AI-WebApp
- Bấm ô chọn nhánh (branch) → chọn **`claude/webapp-purchasing-excel-fu894t`**.
- Bấm nút xanh **Code → Download ZIP** → giải nén ra một thư mục (vd Desktop).
- Link tải trực tiếp bản ZIP:
  `https://github.com/linh-eng/AI-WebApp/archive/refs/heads/claude/webapp-purchasing-excel-fu894t.zip`

## Bước 3: Chạy

- **Chỉ dùng trên máy mình:**
  - Windows: bấm đúp **`run-muahang.bat`**
  - macOS: chạy **`./run-muahang.sh`**
- **Cho cả phòng dùng chung (mạng nội bộ):**
  - Windows: bấm đúp **`run-mang-noi-bo.bat`**
  - macOS: chạy **`./run-mang-noi-bo.sh`**
  - Xem chi tiết ở `HUONG-DAN-TRIEN-KHAI-NOI-BO.md`.

Lần đầu sẽ tự cài thư viện (khoảng 1–2 phút). Sau đó trình duyệt tự mở trang đăng nhập.

## Bước 4: Đăng nhập

- Địa chỉ: **http://127.0.0.1:8010**
- Tài khoản: **admin** — Mật khẩu: **admin123** (đổi ngay ở menu 🔑 Người dùng).

## Tắt ứng dụng

- Đóng cửa sổ đen (Command Prompt/Terminal) hoặc bấm **Ctrl + C** trong đó.

---

## Câu hỏi thường gặp

**Cả phòng dùng chung được không?**
Được. Cài trên một máy luôn bật, chạy `run-mang-noi-bo.bat` — mọi người trong mạng
công ty vào `http://<IP-hoặc-tên-máy>:8010`. Chi tiết: `HUONG-DAN-TRIEN-KHAI-NOI-BO.md`.

**Dữ liệu lưu ở đâu?**
Trong thư mục `data/` (file `thng.db`). Nên sao lưu thư mục này định kỳ.

**Đổi mật khẩu admin?**
Đăng nhập admin → menu **🔑 Người dùng → Sửa** dòng admin → nhập mật khẩu mới → Lưu.

**Bị lỗi khi chạy?**
Chụp màn hình cửa sổ đen báo lỗi gửi em, em xử lý ngay.
