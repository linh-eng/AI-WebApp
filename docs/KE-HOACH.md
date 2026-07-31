# Kế hoạch xây dựng WebApp Báo Cáo Kinh Doanh THNG

> WebApp nội bộ giúp phòng Kinh Doanh nhập dữ liệu và xuất **báo cáo Excel đúng
> theo file mẫu `Mau_bao_cao_kinh_doanh_THNG.xlsx`** của công ty (giữ nguyên
> định dạng, công thức, bố cục).
>
> Trạng thái: **Bản kế hoạch — chờ chị duyệt.** Đã phân tích xong file mẫu.

---

## 1. Mục tiêu

- Nhân viên Kinh Doanh nhập liệu trên web (thay vì gõ trực tiếp Excel).
- Hệ thống tự tính toán (giá sau VAT, công nợ, tiến độ, quá hạn…) như file mẫu.
- Xuất ra file Excel **đúng 100% mẫu THNG** để gửi/ lưu trữ.
- Chạy nội bộ trong công ty, có đăng nhập & phân quyền.

## 2. Phân tích file mẫu (9 sheet)

Quy trình nghiệp vụ: **Báo giá → PO/Hợp đồng → Tiến độ & Chất lượng → Thanh toán → Công nợ**.

### Sheet nhập liệu (nhân viên nhập tay)

| Sheet | Vai trò | Các trường nhập chính |
|-------|---------|------------------------|
| **Khách hàng** | Danh mục KH | Mã KH, Tên, Người liên hệ, ĐT/Email, Điều khoản TT (số ngày), Hạn mức công nợ, Ghi chú |
| **Báo giá** | Sổ theo dõi báo giá | Mã báo giá, Ngày, Mã KH, Nội dung, Giá trước VAT, VAT %, Hiệu lực đến, Trạng thái (Đang chào/Thắng/Thua/Huỷ), Mã PO (khi thắng), NV phụ trách |
| **Hợp đồng** | PO / Hợp đồng + Tiến độ + Chất lượng | Mã PO, Ngày nhận PO, Mã báo giá, Số HĐ, Ngày ký, Giá trị HĐ, Ngày giao cam kết, Ngày giao thực tế, Tình trạng chất lượng, Tỷ lệ hàng lỗi |
| **Thanh toán** | Sổ thu tiền (1 PO thu nhiều đợt) | Mã phiếu thu, Ngày thu, Mã PO, Số tiền thu, Hình thức, Đợt/nội dung |

### Sheet tự động tính (công thức — không nhập tay)

| Sheet | Nội dung tự tính |
|-------|------------------|
| **Công nợ** | Đã thu, Còn phải thu, Số ngày quá hạn, Nhóm tuổi nợ, % đã thu — theo từng PO |
| **Báo cáo tháng** | Tổng hợp số liệu 12 tháng: giá trị báo giá, tỷ lệ thắng, giá trị HĐ, tỷ lệ giao đúng hạn, tiền thu… |
| **Thống kê KH** | Thống kê theo khách hàng |
| **Tổng quan** | Dashboard KPI: số báo giá, tỷ lệ thắng thầu, PO trễ hạn, đã thu / còn phải thu, nợ quá hạn |
| **Hướng dẫn** | Chú thích cách dùng |

### Các phép tính tự động (WebApp phải tái hiện)

- Giá sau VAT = Giá trước VAT × (1 + VAT%).
- Tên KH tự kéo từ Mã KH; Tên KH ở Hợp đồng/Thanh toán tự kéo theo Mã PO/Báo giá.
- Tình trạng tiến độ: *Đúng hạn / Giao trễ / Đang thực hiện / Trễ hạn* (so ngày giao thực tế với ngày cam kết).
- Hạn thanh toán = Ngày giao thực tế + Điều khoản TT của KH.
- Công nợ: Còn phải thu = Giá trị HĐ − Tổng đã thu; Số ngày quá hạn tính theo ngày hiện tại; Nhóm tuổi nợ (Trong hạn / 1-30 / 31-60 / 61-90 / >90 ngày).

> **Cách giữ nguyên định dạng:** dùng chính file `.xlsx` mẫu làm template, code
> chỉ điền dữ liệu vào các ô nhập tay — mọi công thức có sẵn trong file sẽ tự
> tính lại. Không vẽ lại Excel từ đầu.

## 3. Chức năng WebApp theo giai đoạn

### Giai đoạn 1 — MVP (bản chạy được đầu tiên) ✅ ĐÃ XONG
- [x] Đăng nhập tài khoản nội bộ.
- [x] Quản lý **Khách hàng** (thêm/sửa/xoá).
- [x] Nhập **Báo giá**, **Hợp đồng/PO**, **Thanh toán** qua form web (tự tính giá sau VAT, tình trạng, công nợ…).
- [x] Trang **Tổng quan** hiển thị KPI như dashboard file mẫu.
- [x] Nút **Xuất Excel** → sinh ra file đúng mẫu THNG để tải về.

### Giai đoạn 2 ✅ ĐÃ XONG
- [x] **Upload Excel/CSV thô** để nhập nhanh nhiều dòng (thay vì gõ tay).
- [x] Phân quyền: Nhân viên / Trưởng phòng / Admin (+ màn hình quản lý người dùng).
- [x] Bộ lọc theo tháng/năm/khách hàng (danh sách, tổng quan, xuất báo cáo).

### Giai đoạn 3 ✅ ĐÃ XONG
- [x] **Kết nối nguồn dữ liệu ngoài**: đồng bộ tự động từ URL (CSV/JSON) + **REST API** cho phần mềm khác đọc số liệu.
- [x] **Biểu đồ/dashboard trực tiếp trên web** (SVG, chạy offline): diễn biến theo tháng, tỷ lệ thắng thầu/giao đúng hạn, cơ cấu công nợ theo tuổi nợ.
- [x] **Lịch tự động chốt báo cáo** cuối tháng + trang lưu trữ báo cáo đã chốt (tải lại được).

## 4. Công nghệ đề xuất

- **Backend:** Python + **FastAPI**; xử lý Excel bằng **openpyxl** (điền vào file mẫu, giữ nguyên định dạng & công thức).
- **Frontend:** React — form nhập liệu + bảng danh sách, giao diện gọn cho nội bộ.
- **CSDL:** PostgreSQL (hoặc SQLite cho bản demo).
- **Đăng nhập:** JWT + mã hoá mật khẩu (bcrypt), 3 vai trò.
- **Triển khai:** đóng gói **Docker**, chạy trên máy chủ nội bộ; NV truy cập qua địa chỉ nội bộ.

## 5. Mô hình dữ liệu (bảng CSDL, khớp file mẫu)

- `khach_hang` (customers)
- `bao_gia` (quotations) — khoá ngoại tới khach_hang
- `hop_dong` (contracts/PO) — khoá ngoại tới bao_gia
- `thanh_toan` (payments) — khoá ngoại tới hop_dong
- `nguoi_dung` (users) + vai trò
- Công nợ / Báo cáo tháng / Thống kê / Tổng quan = **tính động** khi truy vấn, không lưu.

## 6. Lộ trình & việc cần chị

| Bước | Nội dung |
|------|----------|
| ✅ 0 | Phân tích file mẫu — **đã xong** |
| 1 | Dựng khung dự án + đăng nhập + quản lý Khách hàng |
| 2 | Nhập Báo giá / Hợp đồng / Thanh toán + tính toán tự động |
| 3 | Trang Tổng quan + **Xuất Excel đúng mẫu THNG** |
| 4 | (GĐ2) Upload Excel/CSV + phân quyền |
| 5 | (GĐ3) Kết nối hệ thống có sẵn + dashboard |

**Cần chị xác nhận:**
1. Duyệt kế hoạch & công nghệ ở trên (hoặc điều chỉnh).
2. Số lượng người dùng dự kiến & ai là Admin.
3. (GĐ3) Tên phần mềm/CSDL có sẵn muốn kết nối (nếu có).

---

*Sau khi chị duyệt, em bắt đầu dựng bản MVP (Giai đoạn 1) và đẩy code lên nhánh.*
