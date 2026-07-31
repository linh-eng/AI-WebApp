# WebApp Báo cáo Kinh doanh THNG

Ứng dụng web nội bộ giúp phòng Kinh Doanh nhập liệu và xuất **báo cáo Excel đúng
theo file mẫu THNG** (giữ nguyên định dạng, công thức, bố cục).

Quy trình nghiệp vụ: **Báo giá → PO/Hợp đồng → Tiến độ & Chất lượng → Thanh toán → Công nợ.**

## Tính năng

**Giai đoạn 1 (MVP)**
- Đăng nhập tài khoản nội bộ.
- Quản lý **Khách hàng, Báo giá, Hợp đồng/PO, Thanh toán** (thêm/sửa/xoá).
- Tự động tính: giá sau VAT, tình trạng tiến độ, hạn thanh toán, công nợ, quá hạn…
- Trang **Tổng quan** hiển thị KPI như dashboard file mẫu.
- Nút **Xuất báo cáo Excel** → sinh file `.xlsx` đúng mẫu THNG để tải về.

**Giai đoạn 2**
- **Phân quyền 3 vai trò**: Nhân viên (nhập/sửa) · Trưởng phòng (thêm quyền xoá) ·
  Admin (thêm quyền quản lý người dùng). Có màn hình **Quản lý người dùng** (Admin).
- **Nhập nhanh từ Excel/CSV**: tải file mẫu, điền nhiều dòng rồi upload; trùng mã thì
  cập nhật, mã mới thì thêm.
- **Bộ lọc** theo năm / tháng / khách hàng ở các danh sách; lọc theo năm khi xem
  Tổng quan và khi xuất báo cáo Excel.

**Giai đoạn 3**
- **Biểu đồ trực quan** trên Tổng quan (SVG, chạy offline không cần internet):
  diễn biến theo tháng, tỷ lệ thắng thầu / giao đúng hạn, cơ cấu công nợ theo tuổi nợ.
- **Kết nối nguồn dữ liệu ngoài** (Admin): đồng bộ tự động từ một URL trả CSV/JSON
  (Google Sheets, phần mềm bán hàng/ERP…). Trùng mã → cập nhật, mã mới → thêm.
- **REST API** cho hệ thống khác đọc số liệu (`/api/tong-quan`, `/api/{màn-hình}`),
  bảo vệ bằng `API_TOKEN`.
- **Chốt & lưu báo cáo định kỳ**: nút chốt báo cáo thủ công + **tự động chốt mỗi
  tháng**; trang lưu trữ tải lại file Excel bất kỳ lúc nào.

**Giai đoạn 4 (mở rộng)**
- **Nhắc nợ & cảnh báo tự động** — trang **Cần xử lý** + số cảnh báo trên menu:
  công nợ quá hạn, báo giá sắp/đã hết hiệu lực, PO trễ giao hàng.
- **Danh mục sản phẩm + chi tiết dòng hàng báo giá** (số lượng × đơn giá, tự cộng;
  giá trị trước VAT của báo giá tự cập nhật theo dòng hàng).
- **Xuất PDF báo giá** — file PDF có tiếng Việt, logo/thông tin công ty, gửi thẳng khách.
- **Mục tiêu doanh số (KPI)** — đặt chỉ tiêu theo nhân viên & kỳ, so sánh thực đạt,
  thanh tiến độ % hoàn thành.

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
| `API_TOKEN` | (mẫu) | Token cho REST API — **đổi khi chạy thật** |
| `TU_DONG_CHOT` | `true` | Bật/tắt tự động chốt báo cáo hằng tháng |

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
