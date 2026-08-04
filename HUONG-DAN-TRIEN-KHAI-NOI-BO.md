# Hướng dẫn đưa WebApp cho cả phòng Kinh Doanh dùng chung

Mục tiêu: cài trên **một máy** trong công ty (gọi là "máy chủ"), các nhân viên khác
trong cùng mạng công ty (Wi‑Fi/LAN) mở trình duyệt vào **địa chỉ IP của máy đó** để dùng.

> Ai nên làm việc này: một người phụ trách (hoặc bạn IT). Nhân viên khác chỉ cần
> mở trình duyệt, không phải cài gì.

---

## A. Chọn máy chủ

- Một máy tính **luôn bật trong giờ làm** (máy để bàn của phòng, hoặc một máy chủ nhỏ).
- Máy này cắm dây mạng/Wi‑Fi chung với cả phòng.
- Nên đặt **IP tĩnh** cho máy (nhờ IT) để địa chỉ không đổi mỗi ngày.

## B. Cài & chạy (trên máy chủ, Windows)

1. Cài Python (nếu chưa) — xem `HUONG-DAN-CHAY.md`, nhớ tích **"Add Python to PATH"**.
2. Tải mã nguồn về, giải nén.
3. **Bấm đúp `run-mang-noi-bo.bat`** (KHÁC với `run.bat` — bản này cho cả mạng dùng).
4. Lần đầu Windows hỏi **"Allow access / Cho phép truy cập"** → bấm **Allow** (Cho phép),
   nhớ tích ô **Private networks / Mạng riêng**.
5. Cửa sổ đen sẽ in ra dòng **IPv4 Address** (ví dụ `192.168.1.50`). Ghi lại địa chỉ này.

## C. Nhân viên truy cập

Mở trình duyệt (Chrome/Edge), dùng **một trong hai** địa chỉ (script in sẵn cả hai):

- **Cách dễ nhớ (khuyên dùng khi không có IT):** bằng **tên máy chủ**, ví dụ
  `http://MAY-KINHDOANH:8000`. Ưu điểm: **không đổi** kể cả khi IP thay đổi.
- **Cách bằng IP:** `http://192.168.1.50:8000` (thay bằng IPv4 thật ở bước B5).

Đăng nhập bằng tài khoản do admin cấp.

> Nếu cách tên máy không vào được (một số mạng chặn), dùng cách IP.

## D. Tạo tài khoản cho nhân viên

1. Admin đăng nhập (`admin` / `admin123`).
2. Vào menu **🔑 Người dùng → ＋ Thêm người dùng**.
3. Nhập tài khoản, mật khẩu, chọn vai trò:
   - **Nhân viên**: nhập/sửa dữ liệu.
   - **Trưởng phòng**: thêm quyền xoá.
   - **Admin**: thêm quyền quản lý người dùng & nguồn dữ liệu.

## E. Bảo mật — làm ngay khi chạy thật

1. **Đổi mật khẩu admin**: đăng nhập admin → **Người dùng → Sửa** dòng admin →
   nhập mật khẩu mới → Lưu.
2. Khoá bí mật phiên đăng nhập được **tự sinh riêng** cho mỗi lần cài (lưu ở
   `data/secret.key`) — không cần làm gì thêm.
3. Nếu dùng **REST API**, đặt `API_TOKEN` riêng (xem README).
4. Ứng dụng **chỉ chạy trong mạng nội bộ** — không mở ra internet trừ khi có IT
   cấu hình bảo mật.

## E2. Tự khởi động khi bật máy (khuyến nghị cho máy chủ)

Để mỗi lần bật máy chủ, WebApp tự chạy mà không phải bấm tay:

1. Trong thư mục app, **bấm đúp `cai-tu-khoi-dong.bat`** (chạy một lần).
2. Từ lần sau, khi bật máy và **đăng nhập Windows**, WebApp tự chạy (cửa sổ thu nhỏ
   dưới thanh tác vụ — đừng đóng nó).
3. Muốn tắt tính năng này: chạy **`tat-tu-khoi-dong.bat`**.

> Cách này chạy khi **đăng nhập Windows**. Nếu muốn chạy ngay khi bật máy mà chưa
> đăng nhập, cần bật **tự động đăng nhập (auto-login)** cho máy chủ, hoặc dùng
> **Task Scheduler** (nhờ IT) — báo em nếu cần hướng dẫn.

## F. Sao lưu dữ liệu

- Toàn bộ dữ liệu nằm trong thư mục **`data/`** (file `thng.db`).
- Định kỳ **sao chép thư mục `data/`** sang nơi an toàn (ổ khác/USB/ổ mạng).

## G. Cách chạy ổn định hơn (khuyến nghị nếu có IT)

Dùng **Docker** để ứng dụng tự khởi động lại, chạy nền:

```bash
docker compose up -d --build
```

Đồng nghiệp vào `http://<IP-máy-chủ>:8000`. Dữ liệu lưu trong volume `thng_data`.
Tắt: `docker compose down`.

---

## Câu hỏi thường gặp

**Nhân viên báo "không vào được trang"?**
- Kiểm tra họ có **cùng mạng công ty** với máy chủ không.
- Máy chủ đã chạy `run-mang-noi-bo.bat` chưa (cửa sổ đen còn mở)?
- Windows Firewall trên máy chủ đã **Allow** chưa? Nếu lỡ bấm Cancel: vào
  *Windows Defender Firewall → Allow an app* → cho phép Python.
- Thử đúng địa chỉ `http://<IPv4>:8000` (đúng IPv4, có `:8000`).

**Muốn nhân viên đi công tác / ở nhà cũng vào được?**
- Cần đưa lên internet hoặc dùng **VPN công ty**. Việc này cần IT hỗ trợ về bảo
  mật — báo em, em hướng dẫn phương án phù hợp.

**Địa chỉ IP hay đổi?**
- Nhờ IT đặt **IP tĩnh** cho máy chủ, hoặc đặt một tên nội bộ (DNS nội bộ) để
  nhân viên gõ cho dễ nhớ.
