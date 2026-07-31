# WebApp Báo cáo Kinh doanh THNG

Ứng dụng web nội bộ giúp phòng Kinh Doanh nhập liệu và xuất **báo cáo Excel đúng
theo file mẫu THNG** (giữ nguyên định dạng, công thức, bố cục).

Quy trình nghiệp vụ: **Báo giá → PO/Hợp đồng → Tiến độ & Chất lượng → Thanh toán → Công nợ.**

## Tính năng (bản MVP - Giai đoạn 1)

- Đăng nhập tài khoản nội bộ.
- Quản lý **Khách hàng, Báo giá, Hợp đồng/PO, Thanh toán** (thêm/sửa/xoá).
- Tự động tính: giá sau VAT, tình trạng tiến độ, hạn thanh toán, công nợ, quá hạn…
- Trang **Tổng quan** hiển thị KPI như dashboard file mẫu.
- Nút **Xuất báo cáo Excel** → sinh file `.xlsx` đúng mẫu THNG để tải về.

## Chạy nhanh (không cần Docker)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
# Mở http://127.0.0.1:8000  — đăng nhập admin / admin123
```

## Chạy bằng Docker (khuyến nghị khi triển khai nội bộ)

```bash
docker compose up -d --build
# Mở http://<địa-chỉ-máy-chủ>:8000
```

Dữ liệu SQLite được lưu trong volume `thng_data` (an toàn khi rebuild).

## Cấu hình (biến môi trường)

| Biến | Mặc định | Ý nghĩa |
|------|----------|---------|
| `SECRET_KEY` | (mẫu) | Khoá ký cookie đăng nhập — **bắt buộc đổi khi chạy thật** |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | admin / admin123 | Tài khoản admin khởi tạo lần đầu |
| `DATABASE_URL` | SQLite trong `data/` | Đổi sang PostgreSQL nếu cần |
| `TEMPLATE_XLSX` | `docs/templates/Mau_bao_cao_kinh_doanh_THNG.xlsx` | File Excel mẫu |
| `DATA_DIR` | `data/` | Nơi lưu CSDL SQLite |

## Cách giữ nguyên định dạng Excel

Khi xuất báo cáo, hệ thống mở **chính file mẫu THNG** và chỉ điền dữ liệu vào các
ô nhập tay; toàn bộ công thức, logo, màu sắc, bố cục của file mẫu được giữ nguyên
và tự tính lại khi mở bằng Excel.

## Cấu trúc mã nguồn

```
app/
  main.py           # Route web (đăng nhập, dashboard, CRUD, xuất Excel)
  models.py         # Bảng CSDL (khớp các sheet nhập tay của file mẫu)
  calculations.py   # Tái hiện công thức tự động của file mẫu
  excel_export.py   # Điền dữ liệu vào file mẫu -> xuất .xlsx
  web_meta.py       # Khai báo field cho các form nhập liệu
  security.py       # Băm mật khẩu (PBKDF2)
  seed.py           # Tạo admin + dữ liệu mẫu lần đầu
  templates/ static/# Giao diện
docs/
  KE-HOACH.md       # Kế hoạch & phân tích file mẫu
  templates/*.xlsx  # File Excel mẫu THNG
```

## Lộ trình tiếp theo

- Giai đoạn 2: upload Excel/CSV để nhập nhanh nhiều dòng; phân quyền nhân viên / trưởng phòng / admin.
- Giai đoạn 3: kết nối CSDL/phần mềm có sẵn của công ty; biểu đồ trực tiếp trên web.
