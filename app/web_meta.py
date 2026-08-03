"""Khai báo các trường NHẬP TAY cho từng màn hình (dùng chung cho form web).

Mỗi field: (name, label, type) - type: text|number|date|money|percent|select|textarea
Với select tĩnh dùng key "options"; select động (từ bảng khác) dùng "source".
Chỉ khai báo ô NHẬP TAY của file mẫu; các cột công thức được tính ở calculations.py.
"""

FIELDS_DU_AN = [
    {"name": "ma_du_an", "label": "Mã dự án", "type": "text", "required": True},
    {"name": "ten", "label": "Tên dự án", "type": "text", "required": True},
    {"name": "khach_hang", "label": "Khách hàng / Chủ đầu tư", "type": "text"},
    {"name": "pm", "label": "Quản lý dự án (PM)", "type": "text"},
    {"name": "ngay_bat_dau", "label": "Ngày bắt đầu", "type": "date"},
    {"name": "ngay_ket_thuc", "label": "Ngày kết thúc dự kiến", "type": "date"},
    {"name": "ngan_sach", "label": "Ngân sách mua hàng (VNĐ)", "type": "money"},
    {"name": "trang_thai", "label": "Trạng thái dự án", "type": "select",
     "options": ["Đang thực hiện", "Tạm dừng", "Hoàn thành", "Huỷ"]},
    {"name": "ghi_chu", "label": "Ghi chú", "type": "text"},
]

FIELDS_NHA_CUNG_CAP = [
    {"name": "ma_ncc", "label": "Mã NCC", "type": "text", "required": True},
    {"name": "ten", "label": "Tên nhà cung cấp", "type": "text", "required": True},
    {"name": "nguoi_lien_he", "label": "Người liên hệ", "type": "text"},
    {"name": "dien_thoai", "label": "Điện thoại", "type": "text"},
    {"name": "email", "label": "Email", "type": "text"},
    {"name": "dia_chi", "label": "Địa chỉ", "type": "text"},
    {"name": "dieu_khoan_tt", "label": "Điều khoản TT (số ngày)", "type": "number"},
    {"name": "danh_gia", "label": "Đánh giá NCC", "type": "select",
     "options": ["A", "B", "C", "D"]},
    {"name": "nhom_hang", "label": "Nhóm hàng cung cấp", "type": "text"},
    {"name": "ma_so_thue", "label": "Mã số thuế", "type": "text"},
    {"name": "ghi_chu", "label": "Ghi chú", "type": "text"},
]

FIELDS_CHECK_GIA = [
    {"name": "ma_yc", "label": "Mã YC", "type": "text", "required": True},
    {"name": "ngay_nhan", "label": "Ngày nhận yêu cầu", "type": "date"},
    {"name": "ma_du_an", "label": "Dự án", "type": "select", "source": "du_an"},
    {"name": "nguoi_yc", "label": "Người / Bộ phận yêu cầu", "type": "text"},
    {"name": "hang_muc", "label": "Hạng mục cần check giá", "type": "text"},
    {"name": "dvt", "label": "ĐVT", "type": "text"},
    {"name": "so_luong", "label": "Số lượng", "type": "number"},
    {"name": "don_gia_du_toan", "label": "Đơn giá dự toán (VNĐ)", "type": "money"},
    {"name": "han_tra_gia", "label": "Hạn trả giá", "type": "date"},
    {"name": "ngay_tra_gia", "label": "Ngày trả giá thực tế", "type": "date"},
    {"name": "trang_thai", "label": "Trạng thái xử lý", "type": "select",
     "options": ["", "Mới nhận", "Đang xử lý", "Đã trả giá"]},
    {"name": "ghi_chu", "label": "Ghi chú", "type": "text"},
]

FIELDS_BAO_GIA = [
    {"name": "ma_bao_gia", "label": "Mã báo giá", "type": "text", "required": True},
    {"name": "ngay", "label": "Ngày báo giá", "type": "date"},
    {"name": "ma_yc", "label": "Mã YC (check giá)", "type": "select", "source": "check_gia"},
    {"name": "ma_ncc", "label": "Nhà cung cấp", "type": "select", "source": "nha_cung_cap"},
    {"name": "don_gia", "label": "Đơn giá báo giá (VNĐ)", "type": "money"},
    {"name": "thoi_gian_giao", "label": "Thời gian giao (ngày)", "type": "number"},
    {"name": "hieu_luc", "label": "Hiệu lực báo giá đến", "type": "date"},
    {"name": "duoc_chon", "label": "NCC được chọn", "type": "select",
     "options": ["", "x"]},
    {"name": "ghi_chu", "label": "Ghi chú", "type": "text"},
]

FIELDS_PR = [
    {"name": "ma_pr", "label": "Mã PR", "type": "text", "required": True},
    {"name": "ngay", "label": "Ngày đề nghị", "type": "date"},
    {"name": "ma_yc", "label": "Mã YC (check giá)", "type": "select", "source": "check_gia"},
    {"name": "so_luong", "label": "Số lượng", "type": "number"},
    {"name": "don_gia_du_toan", "label": "Đơn giá dự toán (VNĐ)", "type": "money"},
    {"name": "ngay_can_hang", "label": "Ngày cần hàng", "type": "date"},
    {"name": "trang_thai_duyet", "label": "Trạng thái duyệt", "type": "select",
     "options": ["", "Chờ duyệt", "Đã duyệt", "Từ chối"]},
    {"name": "nguoi_duyet", "label": "Người duyệt", "type": "text"},
    {"name": "ngay_duyet", "label": "Ngày duyệt", "type": "date"},
    {"name": "ghi_chu", "label": "Ghi chú", "type": "text"},
]

FIELDS_PO = [
    {"name": "ma_po", "label": "Mã PO", "type": "text", "required": True},
    {"name": "ngay", "label": "Ngày PO", "type": "date"},
    {"name": "ma_pr", "label": "Mã PR", "type": "select", "source": "pr"},
    {"name": "ma_ncc", "label": "Nhà cung cấp", "type": "select", "source": "nha_cung_cap"},
    {"name": "so_luong_dat", "label": "Số lượng đặt", "type": "number"},
    {"name": "don_gia_po", "label": "Đơn giá PO (VNĐ)", "type": "money"},
    {"name": "so_hop_dong", "label": "Số hợp đồng", "type": "text"},
    {"name": "ngay_ky", "label": "Ngày ký hợp đồng", "type": "date"},
    {"name": "ngay_giao_cam_ket", "label": "Ngày giao cam kết", "type": "date"},
    {"name": "ngay_nhan_thuc_te", "label": "Ngày nhận thực tế", "type": "date"},
    {"name": "sl_nhan", "label": "SL nhận thực tế", "type": "number"},
    {"name": "sl_loi", "label": "SL hàng lỗi", "type": "number"},
    {"name": "sl_tra_lai", "label": "SL trả lại NCC", "type": "number"},
    {"name": "ghi_chu", "label": "Ghi chú", "type": "text"},
]

FIELDS_THANH_TOAN = [
    {"name": "ma_phieu_chi", "label": "Mã phiếu chi", "type": "text", "required": True},
    {"name": "ngay", "label": "Ngày thanh toán", "type": "date"},
    {"name": "ma_po", "label": "Mã PO", "type": "select", "source": "po"},
    {"name": "so_tien", "label": "Số tiền thanh toán (VNĐ)", "type": "money"},
    {"name": "dot", "label": "Đợt thanh toán", "type": "number"},
    {"name": "hinh_thuc", "label": "Hình thức", "type": "select",
     "options": ["Chuyển khoản", "Tiền mặt", "Khác"]},
    {"name": "so_chung_tu", "label": "Số chứng từ NH", "type": "text"},
    {"name": "ghi_chu", "label": "Nội dung / Ghi chú", "type": "text"},
]
