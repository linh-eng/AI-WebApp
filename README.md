# WebApp Báo cáo Mua hàng THNG

Ứng dụng web nội bộ giúp **phòng Mua Hàng** nhập liệu và xuất **báo cáo Excel đúng
theo file mẫu THNG** (giữ nguyên định dạng, công thức, bố cục).

Quy trình nghiệp vụ (3 quy trình như file mẫu):

1. **Check giá:** Dự án → Yêu cầu check giá → Báo giá nhiều NCC → chọn NCC.
2. **PR – PO:** PR (đề nghị mua) → PO/Hợp đồng → theo dõi tiến độ giao & chất lượng.
3. **Thanh toán:** Phiếu chi → Công nợ phải trả (tuổi nợ tự tính).

## Tính năng

- Đăng nhập tài khoản nội bộ, **phân quyền 3 vai trò** (Nhân viên · Trưởng phòng · Admin).
- Quản lý **Dự án, Nhà cung cấp, Check giá, Báo giá, PR, PO, Thanh toán** (thêm/sửa/xoá).
- Tự động tính đúng công thức file mẫu: giá trị dự toán, SLA trả giá, giá chốt,
  tiết kiệm đàm phán, đánh giá giao hàng, tỷ lệ hàng lỗi/đạt, hạn thanh toán,
  công nợ & tuổi nợ (aging)…
- Trang **Tổng quan** hiển thị KPI 6 nhóm (A→F) đúng như sheet "Tổng quan" của file mẫu.
- Trang **Công nợ phải trả** tính động 100% từ PO & phiếu chi.
- Trang **Cần xử lý**: nợ NCC quá hạn, YC quá hạn chưa trả giá, PO trễ giao hàng.
- Nút **Xuất báo cáo Excel** → sinh file `.xlsx` đúng mẫu THNG để tải về.
- **Nhập nhanh từ Excel/CSV** (tải file mẫu, điền nhiều dòng rồi upload; trùng mã → cập nhật).
- **Biểu đồ** trên Tổng quan (SVG, chạy offline): diễn biến theo tháng, tỷ lệ tiết
  kiệm / giao đúng hạn, cơ cấu công nợ theo tuổi nợ.
- **Kết nối nguồn dữ liệu ngoài** (Admin): đồng bộ tự động từ URL CSV/JSON (Google
  Sheets, ERP…). **REST API** (`/api/tong-quan`, `/api/{màn-hình}`) bảo vệ bằng `API_TOKEN`.
- **Chốt & lưu báo cáo định kỳ**: chốt thủ công + tự động chốt mỗi tháng; trang lưu
  trữ tải lại file Excel bất kỳ lúc nào.

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
| `SECRET_KEY` | (tự sinh) | Khoá ký cookie đăng nhập — **đặt cố định khi chạy thật** |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | admin / admin123 | Tài khoản admin khởi tạo lần đầu |
| `DATABASE_URL` | SQLite trong `data/` | Đổi sang PostgreSQL nếu cần |
| `TEMPLATE_XLSX` | `docs/templates/BaoCaoMuaHang_DuAn_THNG.xlsx` | File Excel mẫu |
| `NGUONG_HANG_LOI` | `0.02` | Ngưỡng tỷ lệ hàng lỗi để đánh giá "Đạt" (ô vàng Tổng quan!C8) |
| `DATA_DIR` | `data/` | Nơi lưu CSDL SQLite |
| `API_TOKEN` | (mẫu) | Token cho REST API — **đổi khi chạy thật** |
| `TU_DONG_CHOT` | `true` | Bật/tắt tự động chốt báo cáo hằng tháng |

## Cách giữ nguyên định dạng Excel

Khi xuất báo cáo, hệ thống mở **chính file mẫu THNG** và chỉ điền dữ liệu vào các
ô nhập tay; toàn bộ công thức, màu sắc, bố cục của file mẫu được giữ nguyên và tự
tính lại khi mở bằng Excel (bật `fullCalcOnLoad`).

## Cấu trúc mã nguồn

```
app/
  main.py           # Route web (đăng nhập, dashboard, CRUD, công nợ, xuất Excel, API)
  models.py         # Bảng CSDL (khớp các sheet nhập tay của file mẫu)
  web_meta.py       # Khai báo field nhập tay cho từng màn hình
  calculations.py   # Tái hiện công thức tự động + KPI Tổng quan + công nợ + cảnh báo
  excel_export.py   # Điền dữ liệu vào file mẫu -> xuất .xlsx
  importer.py       # Nhập nhanh Excel/CSV        connectors.py # Đồng bộ URL ngoài
  charts.py         # Biểu đồ SVG offline          security.py   # Băm mật khẩu (PBKDF2)
  seed.py           # Tạo admin + chuỗi dữ liệu mẫu
  templates/ static/# Giao diện
docs/
  KE-HOACH.md       # Kế hoạch & phân tích file mẫu
  templates/*.xlsx  # File Excel mẫu THNG
```

## Sơ đồ liên kết dữ liệu

```
Dự án ─┐
       ├─ Check giá (YC) ──┬─ Báo giá (nhiều NCC, chọn 1 = "x")
NCC ───┘                   └─ PR ── PO ──┬─ Thanh toán
                                         └─ Công nợ phải trả (tính động)
```

Mã ở bước sau phải trùng khớp mã bước trước (VD `DA-2026-01` → `YC-2026-001` →
`BG-2026-001` → `PR-2026-001` → `PO-2026-001` → `PC-2026-001`).
