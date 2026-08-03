"""Khai báo các trường nhập liệu cho từng màn hình (dùng chung cho form web)."""

# Mỗi field: (name, label, type)  - type: text|number|date|money|percent|select|textarea
# Với select tĩnh dùng key "options"; select động (từ bảng khác) dùng "source".

FIELDS_KHACH_HANG = [
    {"name": "ma_kh", "label": "Mã KH", "type": "text", "required": True},
    {"name": "ten", "label": "Tên khách hàng", "type": "text", "required": True},
    {"name": "ma_so_thue", "label": "Mã số thuế", "type": "text"},
    {"name": "dia_chi", "label": "Địa chỉ", "type": "text"},
    {"name": "nguoi_lien_he", "label": "Người liên hệ", "type": "text"},
    {"name": "lien_he", "label": "Điện thoại / Email", "type": "text"},
    {"name": "dieu_khoan_tt", "label": "Điều khoản TT (số ngày)", "type": "number"},
    {"name": "han_muc_cong_no", "label": "Hạn mức công nợ (VNĐ)", "type": "money"},
    {"name": "ghi_chu", "label": "Ghi chú", "type": "text"},
]

FIELDS_BAO_GIA = [
    {"name": "ma_bao_gia", "label": "Mã báo giá", "type": "text", "required": True},
    {"name": "ngay", "label": "Ngày báo giá", "type": "date"},
    {"name": "ma_kh", "label": "Khách hàng", "type": "select", "source": "khach_hang"},
    {"name": "noi_dung", "label": "Nội dung / hạng mục", "type": "text"},
    {"name": "gia_truoc_vat", "label": "Giá trị trước VAT (VNĐ)", "type": "money"},
    {"name": "vat", "label": "VAT (%)", "type": "percent"},
    {"name": "hieu_luc_den", "label": "Hiệu lực đến", "type": "date"},
    {"name": "trang_thai", "label": "Trạng thái", "type": "select",
     "options": ["Đang chào", "Thắng", "Thua", "Huỷ"]},
    {"name": "ma_po", "label": "Mã PO (khi thắng)", "type": "text"},
    {"name": "ngay_chot_don", "label": "Ngày chốt đơn", "type": "date"},
    {"name": "nv_phu_trach", "label": "NV phụ trách", "type": "text"},
    {"name": "ghi_chu", "label": "Ghi chú", "type": "text"},
]

FIELDS_HOP_DONG = [
    {"name": "ma_po", "label": "Mã PO", "type": "text", "required": True},
    {"name": "ngay_nhan_po", "label": "Ngày nhận PO", "type": "date"},
    {"name": "ma_bao_gia", "label": "Mã báo giá", "type": "select", "source": "bao_gia"},
    {"name": "mo_ta_hang_hoa", "label": "Mô tả hàng hóa", "type": "text",
     "derived": "bao_gia:noi_dung"},
    {"name": "vat", "label": "VAT (%)", "type": "percent", "derived": "bao_gia:vat"},
    {"name": "so_luong", "label": "Số lượng", "type": "number"},
    {"name": "don_gia", "label": "Đơn giá (VNĐ)", "type": "money"},
    {"name": "so_hop_dong", "label": "Số hợp đồng", "type": "text"},
    {"name": "ngay_ky", "label": "Ngày ký HĐ", "type": "date"},
    {"name": "gia_tri_hop_dong", "label": "Giá trị hợp đồng (VNĐ)", "type": "money"},
    {"name": "ngay_giao_cam_ket", "label": "Ngày giao cam kết", "type": "date"},
    {"name": "ngay_giao_thuc_te", "label": "Ngày giao thực tế", "type": "date"},
    {"name": "ngay_du_kien_hang_ve", "label": "Ngày dự kiến hàng về", "type": "date"},
    {"name": "ngay_hoa_don", "label": "Ngày hóa đơn", "type": "date"},
    {"name": "cong_no_ngay", "label": "Công nợ (số ngày)", "type": "number"},
    {"name": "tinh_trang_chat_luong", "label": "Tình trạng chất lượng", "type": "select",
     "options": ["", "Đạt", "Lỗi"]},
    {"name": "ty_le_hang_loi", "label": "Tỷ lệ hàng lỗi (%)", "type": "percent"},
    {"name": "ghi_chu", "label": "Ghi chú", "type": "text"},
]

FIELDS_SAN_PHAM = [
    {"name": "ma_sp", "label": "Mã sản phẩm", "type": "text", "required": True},
    {"name": "ten", "label": "Tên sản phẩm", "type": "text", "required": True},
    {"name": "don_vi", "label": "Đơn vị tính", "type": "text"},
    {"name": "don_gia", "label": "Đơn giá (VNĐ)", "type": "money"},
    {"name": "vat", "label": "VAT (%)", "type": "percent"},
    {"name": "mo_ta", "label": "Mô tả", "type": "text"},
]

FIELDS_THANH_TOAN = [
    {"name": "ma_phieu_thu", "label": "Mã phiếu thu", "type": "text", "required": True},
    {"name": "ngay_thu", "label": "Ngày thu", "type": "date"},
    {"name": "ma_po", "label": "Mã PO", "type": "select", "source": "hop_dong"},
    {"name": "so_tien_thu", "label": "Số tiền thu (VNĐ)", "type": "money"},
    {"name": "hinh_thuc", "label": "Hình thức", "type": "select",
     "options": ["Chuyển khoản", "Tiền mặt", "Khác"]},
    {"name": "dot_noi_dung", "label": "Đợt / nội dung", "type": "text"},
]
