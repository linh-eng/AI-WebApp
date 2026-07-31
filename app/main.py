"""Ứng dụng WebApp Báo cáo Kinh doanh THNG (FastAPI + giao diện server-rendered)."""
from __future__ import annotations

from datetime import date, datetime
from urllib.parse import quote

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from fastapi import Header

from . import (calculations, charts, connectors, excel_export, importer, models,
               web_meta)
from .config import API_TOKEN, BASE_DIR, SECRET_KEY, TU_DONG_CHOT
from .database import Base, SessionLocal, engine, get_db
from .security import hash_password, verify_password
from .seed import khoi_tao_du_lieu

# Vai trò người dùng
ROLE_LABELS = {"nhan_vien": "Nhân viên", "truong_phong": "Trưởng phòng", "admin": "Admin"}


def _can_delete(user) -> bool:
    return user.vai_tro in ("truong_phong", "admin")


def _is_admin(user) -> bool:
    return user.vai_tro == "admin"

app = FastAPI(title="WebApp Báo cáo Kinh doanh THNG")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=8 * 3600)
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@app.on_event("startup")
def _startup():
    Base.metadata.create_all(bind=engine)
    khoi_tao_du_lieu()
    if TU_DONG_CHOT:
        import threading
        threading.Thread(target=_scheduler_loop, daemon=True).start()


def _scheduler_loop():
    """Mỗi giờ kiểm tra: nếu sang tháng mới thì tự chốt & lưu 1 báo cáo (1 lần/tháng)."""
    import time

    while True:
        try:
            _auto_chot_neu_can()
        except Exception:
            pass
        time.sleep(3600)


def _auto_chot_neu_can():
    now = datetime.now()
    tag = f"[TĐ {now:%Y-%m}]"  # mỗi tháng dương lịch chỉ chốt tự động 1 lần
    db = SessionLocal()
    try:
        da_co = db.scalar(select(models.BaoCaoLuu).where(
            models.BaoCaoLuu.ten.like(tag + "%")))
        if da_co:
            return
        ten = f"{tag} Báo cáo tự động tháng {now:%m/%Y}"
        _chot_bao_cao(db, str(now.year), ten)
    finally:
        db.close()


# ---- Bộ lọc hiển thị cho template ---------------------------------------

def _money(v):
    try:
        return f"{float(v):,.0f}".replace(",", ".")
    except (TypeError, ValueError):
        return v


def _percent(v):
    try:
        return f"{float(v) * 100:.1f}%"
    except (TypeError, ValueError):
        return v


def _ngay(v):
    return v.strftime("%d/%m/%Y") if isinstance(v, (date, datetime)) else (v or "")


templates.env.filters["money"] = _money
templates.env.filters["percent"] = _percent
templates.env.filters["ngay"] = _ngay
# Cho template dùng để hiển thị theo quyền
templates.env.globals["can_delete"] = _can_delete
templates.env.globals["is_admin"] = _is_admin
templates.env.globals["ROLE_LABELS"] = ROLE_LABELS


# ---- Xác thực đăng nhập -------------------------------------------------

def current_user(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("uid")
    if not uid:
        return None
    return db.get(models.NguoiDung, uid)


def require_login(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return None
    return user


def _redirect_login():
    return RedirectResponse("/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_form(request: Request, loi: str = ""):
    return templates.TemplateResponse(request, "login.html", {"request": request, "loi": loi})


@app.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...),
          db: Session = Depends(get_db)):
    user = db.scalar(select(models.NguoiDung).where(models.NguoiDung.username == username))
    if not user or not verify_password(password, user.mat_khau_hash):
        return RedirectResponse("/login?loi=1", status_code=303)
    request.session["uid"] = user.id
    return RedirectResponse("/", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)


# ---- Trang Tổng quan (dashboard) ----------------------------------------

def _nam_cua(rec, attr) -> int | None:
    v = getattr(rec, attr, None)
    return v.year if isinstance(v, (date, datetime)) else None


def _loc_nam(records, attr, nam):
    """Lọc bản ghi theo năm của trường ngày `attr`. nam=None -> lấy tất cả."""
    if not nam:
        return list(records)
    return [r for r in records if _nam_cua(r, attr) == nam]


def _danh_sach_nam(bao_gias, hop_dongs, thanh_toans) -> list[int]:
    nams = set()
    for r in bao_gias:
        nams.add(_nam_cua(r, "ngay"))
    for r in hop_dongs:
        nams.add(_nam_cua(r, "ngay_ky"))
    for r in thanh_toans:
        nams.add(_nam_cua(r, "ngay_thu"))
    return sorted(n for n in nams if n)


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, nam: int | None = None, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    khachs = db.scalars(select(models.KhachHang)).all()
    bao_gias = db.scalars(select(models.BaoGia)).all()
    hop_dongs = db.scalars(select(models.HopDong)).all()
    thanh_toans = db.scalars(select(models.ThanhToan)).all()
    cac_nam = _danh_sach_nam(bao_gias, hop_dongs, thanh_toans)

    bg_loc = _loc_nam(bao_gias, "ngay", nam)
    hd_loc = _loc_nam(hop_dongs, "ngay_ky", nam)
    tt_loc = _loc_nam(thanh_toans, "ngay_thu", nam)
    tq = calculations.tong_quan(khachs, bg_loc, hd_loc, tt_loc)

    # Biểu đồ (SVG server-side)
    svg_thang = charts.bieu_do_thang(calculations.dien_bien_thang(hd_loc, tt_loc))
    svg_no = charts.bieu_do_tuoi_no(
        calculations.co_cau_tuoi_no(khachs, bg_loc, hd_loc, tt_loc))
    svg_thang_thau = charts.bieu_do_vong(tq["ty_le_thang"], "Thắng thầu")
    svg_dung_han = charts.bieu_do_vong(tq["ty_le_giao_dung_han"], "Giao đúng hạn")

    return templates.TemplateResponse(request, "dashboard.html", {
        "request": request, "user": user, "tq": tq, "active": "dashboard",
        "cac_nam": cac_nam, "nam_chon": nam,
        "svg_thang": svg_thang, "svg_no": svg_no,
        "svg_thang_thau": svg_thang_thau, "svg_dung_han": svg_dung_han,
    })


# ---- Xuất báo cáo Excel -------------------------------------------------

@app.get("/xuat-excel")
def xuat_excel(request: Request, nam: int | None = None, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    data = excel_export.xuat_bao_cao(
        db.scalars(select(models.KhachHang)).all(),
        _loc_nam(db.scalars(select(models.BaoGia)).all(), "ngay", nam),
        _loc_nam(db.scalars(select(models.HopDong)).all(), "ngay_ky", nam),
        _loc_nam(db.scalars(select(models.ThanhToan)).all(), "ngay_thu", nam),
    )
    hau_to = f"_{nam}" if nam else ""
    ten = f"Bao_cao_kinh_doanh_THNG{hau_to}_{date.today():%Y%m%d}.xlsx"
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{ten}"'},
    )


# ---- Quản lý người dùng (chỉ Admin) -------------------------------------

@app.get("/nguoi-dung", response_class=HTMLResponse)
def nguoi_dung_list(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    if not _is_admin(user):
        return RedirectResponse("/", status_code=303)
    users = db.scalars(select(models.NguoiDung)).all()
    return templates.TemplateResponse(request, "nguoi_dung_list.html", {
        "request": request, "user": user, "active": "nguoi-dung", "users": users,
    })


@app.get("/nguoi-dung/them", response_class=HTMLResponse)
def nguoi_dung_them(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user or not _is_admin(user):
        return _redirect_login() if not user else RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(request, "nguoi_dung_form.html", {
        "request": request, "user": user, "active": "nguoi-dung",
        "obj": None, "is_edit": False,
    })


@app.get("/nguoi-dung/sua/{uid}", response_class=HTMLResponse)
def nguoi_dung_sua(uid: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user or not _is_admin(user):
        return _redirect_login() if not user else RedirectResponse("/", status_code=303)
    obj = db.get(models.NguoiDung, uid)
    if not obj:
        return RedirectResponse("/nguoi-dung", status_code=303)
    return templates.TemplateResponse(request, "nguoi_dung_form.html", {
        "request": request, "user": user, "active": "nguoi-dung",
        "obj": obj, "is_edit": True,
    })


@app.post("/nguoi-dung/luu")
async def nguoi_dung_luu(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user or not _is_admin(user):
        return _redirect_login() if not user else RedirectResponse("/", status_code=303)
    form = await request.form()
    uid = form.get("_uid")
    username = (form.get("username") or "").strip()
    ho_ten = (form.get("ho_ten") or "").strip()
    vai_tro = form.get("vai_tro") or "nhan_vien"
    mat_khau = (form.get("mat_khau") or "").strip()

    if uid:  # sửa
        obj = db.get(models.NguoiDung, int(uid))
        if not obj:
            return RedirectResponse("/nguoi-dung", status_code=303)
        obj.username = username or obj.username
        obj.ho_ten = ho_ten
        obj.vai_tro = vai_tro
        if mat_khau:  # chỉ đổi khi có nhập mật khẩu mới
            obj.mat_khau_hash = hash_password(mat_khau)
    else:  # thêm mới
        if not username or not mat_khau:
            msg = quote("Cần nhập tài khoản và mật khẩu.")
            return RedirectResponse(f"/nguoi-dung/them?loi={msg}", status_code=303)
        obj = models.NguoiDung(
            username=username, ho_ten=ho_ten, vai_tro=vai_tro,
            mat_khau_hash=hash_password(mat_khau))
        db.add(obj)
    try:
        db.commit()
    except Exception:
        db.rollback()
        msg = quote("Tài khoản đã tồn tại.")
        return RedirectResponse(f"/nguoi-dung/them?loi={msg}", status_code=303)
    return RedirectResponse("/nguoi-dung", status_code=303)


@app.post("/nguoi-dung/xoa/{uid}")
def nguoi_dung_xoa(uid: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user or not _is_admin(user):
        return _redirect_login() if not user else RedirectResponse("/", status_code=303)
    obj = db.get(models.NguoiDung, uid)
    if obj and obj.id != user.id:  # không tự xoá chính mình
        db.delete(obj)
        db.commit()
    return RedirectResponse("/nguoi-dung", status_code=303)


# ---- Bộ khung CRUD dùng chung -------------------------------------------

ENTITIES = {
    "khach-hang": {
        "model": models.KhachHang, "pk": "ma_kh", "title": "Khách hàng",
        "fields": web_meta.FIELDS_KHACH_HANG,
    },
    "bao-gia": {
        "model": models.BaoGia, "pk": "ma_bao_gia", "title": "Báo giá",
        "fields": web_meta.FIELDS_BAO_GIA,
    },
    "hop-dong": {
        "model": models.HopDong, "pk": "ma_po", "title": "Hợp đồng / PO",
        "fields": web_meta.FIELDS_HOP_DONG,
    },
    "thanh-toan": {
        "model": models.ThanhToan, "pk": "ma_phieu_thu", "title": "Thanh toán",
        "fields": web_meta.FIELDS_THANH_TOAN,
    },
    "san-pham": {
        "model": models.SanPham, "pk": "ma_sp", "title": "Sản phẩm",
        "fields": web_meta.FIELDS_SAN_PHAM,
    },
}


# Trường ngày dùng để lọc theo năm/tháng; và entity có cột mã KH trực tiếp
FILTER_DATE = {"bao-gia": "ngay", "hop-dong": "ngay_ky", "thanh-toan": "ngay_thu"}
FILTER_KH = {"bao-gia": "ma_kh"}


def _select_options(db: Session, source: str) -> list[tuple[str, str]]:
    """Danh sách (giá trị, nhãn) cho select động lấy từ bảng khác."""
    if source == "khach_hang":
        return [(k.ma_kh, f"{k.ma_kh} - {k.ten}")
                for k in db.scalars(select(models.KhachHang)).all()]
    if source == "bao_gia":
        return [(b.ma_bao_gia, f"{b.ma_bao_gia} - {b.noi_dung}")
                for b in db.scalars(select(models.BaoGia)).all()]
    if source == "hop_dong":
        return [(h.ma_po, f"{h.ma_po} - {h.so_hop_dong}")
                for h in db.scalars(select(models.HopDong)).all()]
    if source == "san_pham":
        return [(s.ma_sp, f"{s.ma_sp} - {s.ten}")
                for s in db.scalars(select(models.SanPham)).all()]
    return []


def _parse_value(field: dict, raw: str):
    t = field["type"]
    raw = (raw or "").strip()
    if t in ("money", "number"):
        if raw == "":
            return 0
        raw = raw.replace(".", "").replace(",", ".").replace(" ", "")
        try:
            return float(raw)
        except ValueError:
            return 0
    if t == "percent":
        if raw == "":
            return 0
        try:
            return float(raw.replace(",", ".")) / 100.0
        except ValueError:
            return 0
    if t == "date":
        for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(raw, fmt).date()
            except ValueError:
                continue
        return None
    return raw


def _fields_with_options(db: Session, fields: list[dict]) -> list[dict]:
    out = []
    for f in fields:
        f = dict(f)
        if f.get("source"):
            f["options"] = [v for v, _ in _select_options(db, f["source"])]
            f["option_labels"] = dict(_select_options(db, f["source"]))
        out.append(f)
    return out


def _display_value(field: dict, value):
    t = field["type"]
    if value is None:
        return ""
    if t == "money":
        return _money(value)
    if t == "percent":
        return _percent(value)
    if t == "date":
        return _ngay(value)
    return value


# ---- Helper: upsert danh sách bản ghi (dùng cho nhập file & đồng bộ URL) --

def _upsert_records(db: Session, ent: dict, records: list[dict]) -> dict:
    kq = {"them": 0, "cap_nhat": 0, "bo_qua": 0, "loi": None}
    field_by_name = {f["name"]: f for f in ent["fields"]}
    pk = ent["pk"]
    for rec in records:
        ma = str(rec.get(pk) or "").strip()
        if not ma:
            kq["bo_qua"] += 1
            continue
        obj = db.scalar(select(ent["model"]).where(getattr(ent["model"], pk) == ma))
        moi = obj is None
        if moi:
            obj = ent["model"]()
            db.add(obj)
        for name, raw in rec.items():
            f = field_by_name.get(name)
            if f:
                setattr(obj, name, importer.coerce(f, raw))
        kq["them" if moi else "cap_nhat"] += 1
    try:
        db.commit()
    except Exception:
        db.rollback()
        return {"them": 0, "cap_nhat": 0, "bo_qua": 0,
                "loi": "Lỗi khi lưu (mã trùng hoặc dữ liệu không hợp lệ)."}
    return kq


# ---- Kết nối nguồn dữ liệu ngoài (Admin) --------------------------------

def _lay_nguon(db: Session, slug: str) -> models.NguonDuLieu:
    ng = db.scalar(select(models.NguonDuLieu).where(models.NguonDuLieu.slug == slug))
    if not ng:
        ng = models.NguonDuLieu(slug=slug, url="", dinh_dang="csv", bat=False)
        db.add(ng)
        db.commit()
    return ng


@app.get("/nguon-du-lieu", response_class=HTMLResponse)
def nguon_list(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    if not _is_admin(user):
        return RedirectResponse("/", status_code=303)
    nguons = [{"ent": ENTITIES[s], "slug": s, "cfg": _lay_nguon(db, s)} for s in ENTITIES]
    return templates.TemplateResponse(request, "nguon_du_lieu.html", {
        "request": request, "user": user, "active": "nguon-du-lieu", "nguons": nguons,
    })


@app.post("/nguon-du-lieu/luu")
async def nguon_luu(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user or not _is_admin(user):
        return _redirect_login() if not user else RedirectResponse("/", status_code=303)
    form = await request.form()
    for slug in ENTITIES:
        ng = _lay_nguon(db, slug)
        ng.url = (form.get(f"url_{slug}") or "").strip()
        ng.dinh_dang = form.get(f"dinh_dang_{slug}") or "csv"
        ng.bat = form.get(f"bat_{slug}") == "on"
    db.commit()
    return RedirectResponse("/nguon-du-lieu", status_code=303)


@app.post("/nguon-du-lieu/dong-bo/{slug}")
def nguon_dong_bo(slug: str, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user or not _is_admin(user):
        return _redirect_login() if not user else RedirectResponse("/", status_code=303)
    if slug not in ENTITIES:
        return RedirectResponse("/nguon-du-lieu", status_code=303)
    ent = ENTITIES[slug]
    ng = _lay_nguon(db, slug)
    records, loi = connectors.doc_tu_url(ng.url, ng.dinh_dang, ent["fields"])
    if loi:
        ng.ket_qua_cuoi = f"Lỗi: {loi}"
    else:
        kq = _upsert_records(db, ent, records)
        if kq["loi"]:
            ng.ket_qua_cuoi = kq["loi"]
        else:
            ng.ket_qua_cuoi = (f"Thêm {kq['them']} · cập nhật {kq['cap_nhat']} "
                               f"· bỏ qua {kq['bo_qua']}")
    ng.lan_cuoi = datetime.now()
    db.commit()
    return RedirectResponse("/nguon-du-lieu", status_code=303)


# ---- REST API cho phần mềm khác đọc số liệu -----------------------------

def _kiem_tra_token(token: str | None) -> bool:
    return bool(token) and token == API_TOKEN


@app.get("/api/tong-quan")
def api_tong_quan(x_api_token: str | None = Header(default=None),
                  token: str | None = None, db: Session = Depends(get_db)):
    if not _kiem_tra_token(x_api_token or token):
        return Response('{"loi":"Sai token"}', status_code=401,
                        media_type="application/json")
    tq = calculations.tong_quan(
        db.scalars(select(models.KhachHang)).all(),
        db.scalars(select(models.BaoGia)).all(),
        db.scalars(select(models.HopDong)).all(),
        db.scalars(select(models.ThanhToan)).all(),
    )
    return tq


@app.get("/api/{slug}")
def api_list(slug: str, x_api_token: str | None = Header(default=None),
             token: str | None = None, db: Session = Depends(get_db)):
    if not _kiem_tra_token(x_api_token or token):
        return Response('{"loi":"Sai token"}', status_code=401,
                        media_type="application/json")
    if slug not in ENTITIES:
        return Response('{"loi":"Không có dữ liệu"}', status_code=404,
                        media_type="application/json")
    ent = ENTITIES[slug]
    records = db.scalars(select(ent["model"])).all()
    out = []
    for r in records:
        row = {}
        for f in ent["fields"]:
            v = getattr(r, f["name"])
            row[f["name"]] = v.isoformat() if isinstance(v, (date, datetime)) else v
        out.append(row)
    return out


# ---- Chốt & lưu báo cáo định kỳ -----------------------------------------

def _chot_bao_cao(db: Session, ky: str, ten: str) -> models.BaoCaoLuu:
    """Sinh file Excel hiện tại và lưu vào CSDL. ky rỗng = toàn bộ."""
    nam = int(ky) if ky.isdigit() else None
    data = excel_export.xuat_bao_cao(
        db.scalars(select(models.KhachHang)).all(),
        _loc_nam(db.scalars(select(models.BaoGia)).all(), "ngay", nam),
        _loc_nam(db.scalars(select(models.HopDong)).all(), "ngay_ky", nam),
        _loc_nam(db.scalars(select(models.ThanhToan)).all(), "ngay_thu", nam),
    )
    bc = models.BaoCaoLuu(ten=ten, ky=ky, thoi_gian=datetime.now(),
                          so_byte=len(data), du_lieu=data)
    db.add(bc)
    db.commit()
    return bc


@app.get("/bao-cao-luu", response_class=HTMLResponse)
def bao_cao_luu_list(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    items = db.scalars(select(models.BaoCaoLuu).order_by(
        models.BaoCaoLuu.id.desc())).all()
    return templates.TemplateResponse(request, "bao_cao_luu.html", {
        "request": request, "user": user, "active": "bao-cao-luu", "items": items,
    })


@app.post("/bao-cao-luu/chot")
async def bao_cao_luu_chot(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    form = await request.form()
    ky = (form.get("ky") or "").strip()
    if ky and not ky.isdigit():
        ky = ""
    ten = f"Báo cáo {'năm ' + ky if ky else 'toàn bộ'} (chốt {datetime.now():%d/%m/%Y %H:%M})"
    _chot_bao_cao(db, ky, ten)
    return RedirectResponse("/bao-cao-luu", status_code=303)


@app.get("/bao-cao-luu/tai/{bid}")
def bao_cao_luu_tai(bid: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    bc = db.get(models.BaoCaoLuu, bid)
    if not bc:
        return RedirectResponse("/bao-cao-luu", status_code=303)
    ten = f"{bc.ky or 'toanbo'}_{bc.id}.xlsx"
    return Response(
        content=bc.du_lieu,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="Bao_cao_{ten}"'},
    )


@app.post("/bao-cao-luu/xoa/{bid}")
def bao_cao_luu_xoa(bid: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user or not _can_delete(user):
        return _redirect_login() if not user else RedirectResponse("/bao-cao-luu", status_code=303)
    bc = db.get(models.BaoCaoLuu, bid)
    if bc:
        db.delete(bc)
        db.commit()
    return RedirectResponse("/bao-cao-luu", status_code=303)


# ---- Module: Chi tiết dòng hàng của Báo giá -----------------------------

def _cap_nhat_tong_bao_gia(db: Session, ma_bao_gia: str):
    """Cập nhật giá trị trước VAT của báo giá = tổng các dòng hàng (nếu có)."""
    dongs = db.scalars(select(models.BaoGiaDong).where(
        models.BaoGiaDong.ma_bao_gia == ma_bao_gia)).all()
    if not dongs:
        return
    tong = sum((d.so_luong or 0) * (d.don_gia or 0) for d in dongs)
    bg = db.scalar(select(models.BaoGia).where(models.BaoGia.ma_bao_gia == ma_bao_gia))
    if bg:
        bg.gia_truoc_vat = tong
        db.commit()


@app.get("/bao-gia/{ma}/chi-tiet", response_class=HTMLResponse)
def bg_chi_tiet(ma: str, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    bg = db.scalar(select(models.BaoGia).where(models.BaoGia.ma_bao_gia == ma))
    if not bg:
        return RedirectResponse("/bao-gia", status_code=303)
    dongs = db.scalars(select(models.BaoGiaDong).where(
        models.BaoGiaDong.ma_bao_gia == ma)).all()
    san_phams = db.scalars(select(models.SanPham)).all()
    tong = sum((d.so_luong or 0) * (d.don_gia or 0) for d in dongs)
    return templates.TemplateResponse(request, "bao_gia_chi_tiet.html", {
        "request": request, "user": user, "active": "bao-gia", "bg": bg,
        "dongs": dongs, "san_phams": san_phams, "tong": tong,
    })


@app.post("/bao-gia/{ma}/chi-tiet/them")
async def bg_chi_tiet_them(ma: str, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    form = await request.form()
    d = models.BaoGiaDong(
        ma_bao_gia=ma,
        ma_sp=(form.get("ma_sp") or "").strip(),
        ten_hang=(form.get("ten_hang") or "").strip(),
        don_vi=(form.get("don_vi") or "").strip(),
        so_luong=importer.coerce({"type": "number"}, form.get("so_luong")),
        don_gia=importer.coerce({"type": "money"}, form.get("don_gia")),
        ghi_chu=(form.get("ghi_chu") or "").strip(),
    )
    db.add(d)
    db.commit()
    _cap_nhat_tong_bao_gia(db, ma)
    return RedirectResponse(f"/bao-gia/{ma}/chi-tiet", status_code=303)


@app.post("/bao-gia/{ma}/chi-tiet/xoa/{did}")
def bg_chi_tiet_xoa(ma: str, did: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    d = db.get(models.BaoGiaDong, did)
    if d and d.ma_bao_gia == ma:
        db.delete(d)
        db.commit()
        _cap_nhat_tong_bao_gia(db, ma)
    return RedirectResponse(f"/bao-gia/{ma}/chi-tiet", status_code=303)


# ---- Module: Xuất PDF báo giá -------------------------------------------

@app.get("/bao-gia/{ma}/pdf")
def bg_pdf(ma: str, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    bg = db.scalar(select(models.BaoGia).where(models.BaoGia.ma_bao_gia == ma))
    if not bg:
        return RedirectResponse("/bao-gia", status_code=303)
    khach = db.scalar(select(models.KhachHang).where(models.KhachHang.ma_kh == bg.ma_kh))
    dongs = db.scalars(select(models.BaoGiaDong).where(
        models.BaoGiaDong.ma_bao_gia == ma)).all()
    from . import pdf_export
    data = pdf_export.xuat_pdf_bao_gia(bg, khach, dongs)
    return Response(content=data, media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="BaoGia_{ma}.pdf"'})


# ---- Module: Nhắc nợ & cảnh báo (Cần xử lý) -----------------------------

def _tinh_canh_bao(db: Session) -> dict:
    return calculations.canh_bao(
        db.scalars(select(models.KhachHang)).all(),
        db.scalars(select(models.BaoGia)).all(),
        db.scalars(select(models.HopDong)).all(),
        db.scalars(select(models.ThanhToan)).all(),
    )


def _so_canh_bao() -> int:
    db = SessionLocal()
    try:
        return _tinh_canh_bao(db)["tong"]
    except Exception:
        return 0
    finally:
        db.close()


templates.env.globals["so_canh_bao"] = _so_canh_bao


@app.get("/can-xu-ly", response_class=HTMLResponse)
def can_xu_ly(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    cb = _tinh_canh_bao(db)
    return templates.TemplateResponse(request, "can_xu_ly.html", {
        "request": request, "user": user, "active": "can-xu-ly", "cb": cb,
    })


# ---- Module: Mục tiêu doanh số (KPI) ------------------------------------

@app.get("/muc-tieu", response_class=HTMLResponse)
def muc_tieu_view(request: Request, nam: int | None = None,
                  db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    bao_gias = db.scalars(select(models.BaoGia)).all()
    hop_dongs = db.scalars(select(models.HopDong)).all()
    muc_tieus = db.scalars(select(models.MucTieu)).all()
    cac_nam = sorted({m.nam for m in muc_tieus} |
                     {h.ngay_ky.year for h in hop_dongs if h.ngay_ky})
    if nam is None:
        nam = cac_nam[-1] if cac_nam else date.today().year
    rows = calculations.bao_cao_muc_tieu(muc_tieus, bao_gias, hop_dongs, nam)
    ds_nv = sorted({(b.nv_phu_trach or "").strip()
                    for b in bao_gias if (b.nv_phu_trach or "").strip()})
    # Tổng chỉ tiêu: ưu tiên các dòng "cả năm"; nếu không có thì cộng tất cả.
    dong_ca_nam = [r for r in rows if r["thang"] == 0]
    tong_ct = (sum(r["chi_tieu"] for r in dong_ca_nam) if dong_ca_nam
               else sum(r["chi_tieu"] for r in rows))
    # Tổng thực đạt theo năm (không đếm trùng): tổng giá trị HĐ ký trong năm.
    thuc_dat_map = calculations.thuc_dat_theo_nv(bao_gias, hop_dongs, nam)
    tong_dat = sum(m.get(0, 0) for m in thuc_dat_map.values())
    return templates.TemplateResponse(request, "muc_tieu.html", {
        "request": request, "user": user, "active": "muc-tieu", "rows": rows,
        "cac_nam": cac_nam, "nam_chon": nam, "ds_nv": ds_nv,
        "tong_ct": tong_ct, "tong_dat": tong_dat,
        "phan_tram_chung": (tong_dat / tong_ct) if tong_ct else 0,
        "can_sua": _can_delete(user),
    })


@app.post("/muc-tieu/luu")
async def muc_tieu_luu(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    if not _can_delete(user):  # Nhân viên không được đặt mục tiêu
        return RedirectResponse("/muc-tieu", status_code=303)
    form = await request.form()
    nv = (form.get("nv") or "").strip()
    try:
        nam = int(form.get("nam"))
        thang = int(form.get("thang") or 0)
    except (TypeError, ValueError):
        return RedirectResponse("/muc-tieu", status_code=303)
    chi_tieu = importer.coerce({"type": "money"}, form.get("chi_tieu"))
    if not nv:
        return RedirectResponse("/muc-tieu", status_code=303)
    # Trùng (nv, năm, tháng) thì cập nhật
    mt = db.scalar(select(models.MucTieu).where(
        models.MucTieu.nv == nv, models.MucTieu.nam == nam,
        models.MucTieu.thang == thang))
    if not mt:
        mt = models.MucTieu(nv=nv, nam=nam, thang=thang)
        db.add(mt)
    mt.chi_tieu = chi_tieu
    db.commit()
    return RedirectResponse(f"/muc-tieu?nam={nam}", status_code=303)


@app.post("/muc-tieu/xoa/{mid}")
def muc_tieu_xoa(mid: int, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user or not _can_delete(user):
        return _redirect_login() if not user else RedirectResponse("/muc-tieu", status_code=303)
    mt = db.get(models.MucTieu, mid)
    nam = mt.nam if mt else ""
    if mt:
        db.delete(mt)
        db.commit()
    return RedirectResponse(f"/muc-tieu?nam={nam}", status_code=303)


# ---- Bộ khung CRUD chung theo /{slug} (đăng ký CUỐI để không che route cụ thể) ----

@app.get("/{slug}", response_class=HTMLResponse)
def list_view(slug: str, request: Request, nam: int | None = None,
              thang: int | None = None, ma_kh: str = "",
              db: Session = Depends(get_db)):
    if slug not in ENTITIES:
        return _redirect_login() if slug != "favicon.ico" else Response(status_code=404)
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    ent = ENTITIES[slug]
    records = list(db.scalars(select(ent["model"])).all())
    fields = ent["fields"]

    # Bộ lọc theo năm / tháng (theo trường ngày của entity) và theo khách hàng
    date_attr = FILTER_DATE.get(slug)
    kh_attr = FILTER_KH.get(slug)
    cac_nam = []
    if date_attr:
        cac_nam = sorted({_nam_cua(r, date_attr) for r in records
                          if _nam_cua(r, date_attr)})
        if nam:
            records = [r for r in records if _nam_cua(r, date_attr) == nam]
        if thang:
            records = [r for r in records
                       if getattr(r, date_attr) and getattr(r, date_attr).month == thang]
    if kh_attr and ma_kh:
        records = [r for r in records if getattr(r, kh_attr) == ma_kh]

    rows = []
    for rec in records:
        cells = [_display_value(f, getattr(rec, f["name"])) for f in fields]
        rows.append({"pk": getattr(rec, ent["pk"]), "cells": cells})

    return templates.TemplateResponse(request, "list.html", {
        "request": request, "user": user, "slug": slug, "active": slug,
        "title": ent["title"], "headers": [f["label"] for f in fields], "rows": rows,
        "co_loc_ngay": bool(date_attr), "co_loc_kh": bool(kh_attr),
        "cac_nam": cac_nam, "nam_chon": nam, "thang_chon": thang,
        "ds_khach": _select_options(db, "khach_hang") if kh_attr else [],
        "kh_chon": ma_kh,
    })


@app.get("/{slug}/them", response_class=HTMLResponse)
def new_form(slug: str, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    if slug not in ENTITIES:
        return RedirectResponse("/", status_code=303)
    ent = ENTITIES[slug]
    return templates.TemplateResponse(request, "form.html", {
        "request": request, "user": user, "slug": slug, "active": slug,
        "title": ent["title"], "fields": _fields_with_options(db, ent["fields"]),
        "obj": None, "is_edit": False,
    })


@app.get("/{slug}/sua/{pk}", response_class=HTMLResponse)
def edit_form(slug: str, pk: str, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    if slug not in ENTITIES:
        return RedirectResponse("/", status_code=303)
    ent = ENTITIES[slug]
    obj = db.scalar(select(ent["model"]).where(getattr(ent["model"], ent["pk"]) == pk))
    if not obj:
        return RedirectResponse(f"/{slug}", status_code=303)
    values = {}
    for f in ent["fields"]:
        v = getattr(obj, f["name"])
        if f["type"] == "percent" and v is not None:
            v = round(v * 100, 4)
        elif f["type"] == "date" and v is not None:
            v = v.strftime("%Y-%m-%d")
        values[f["name"]] = v
    return templates.TemplateResponse(request, "form.html", {
        "request": request, "user": user, "slug": slug, "active": slug,
        "title": ent["title"], "fields": _fields_with_options(db, ent["fields"]),
        "obj": values, "is_edit": True, "pk": pk,
    })


@app.post("/{slug}/luu")
async def save(slug: str, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    if slug not in ENTITIES:
        return RedirectResponse("/", status_code=303)
    ent = ENTITIES[slug]
    form = await request.form()
    pk_val = (form.get(ent["pk"]) or "").strip()
    is_edit = form.get("_is_edit") == "1"
    orig_pk = form.get("_pk", pk_val)

    if is_edit:
        obj = db.scalar(select(ent["model"]).where(getattr(ent["model"], ent["pk"]) == orig_pk))
        if not obj:
            return RedirectResponse(f"/{slug}", status_code=303)
    else:
        obj = ent["model"]()
        db.add(obj)

    for f in ent["fields"]:
        setattr(obj, f["name"], _parse_value(f, form.get(f["name"], "")))

    try:
        db.commit()
    except Exception:
        db.rollback()
        msg = quote("Mã bị trùng hoặc dữ liệu không hợp lệ.")
        return RedirectResponse(f"/{slug}/them?loi={msg}", status_code=303)
    return RedirectResponse(f"/{slug}", status_code=303)


@app.post("/{slug}/xoa/{pk}")
def delete(slug: str, pk: str, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    if slug not in ENTITIES:
        return RedirectResponse("/", status_code=303)
    if not _can_delete(user):  # Nhân viên không được xoá
        return RedirectResponse(f"/{slug}", status_code=303)
    ent = ENTITIES[slug]
    obj = db.scalar(select(ent["model"]).where(getattr(ent["model"], ent["pk"]) == pk))
    if obj:
        db.delete(obj)
        db.commit()
    return RedirectResponse(f"/{slug}", status_code=303)


# ---- Nhập nhanh từ Excel / CSV ------------------------------------------

@app.get("/{slug}/mau-nhap")
def tai_file_mau(slug: str, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    if slug not in ENTITIES:
        return RedirectResponse("/", status_code=303)
    ent = ENTITIES[slug]
    data = importer.tao_file_mau(ent["fields"], ent["pk"])
    ten = f"Mau_nhap_{slug}.csv"
    return Response(content=data, media_type="text/csv",
                    headers={"Content-Disposition": f'attachment; filename="{ten}"'})


@app.get("/{slug}/nhap", response_class=HTMLResponse)
def import_form(slug: str, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    if slug not in ENTITIES:
        return RedirectResponse("/", status_code=303)
    ent = ENTITIES[slug]
    return templates.TemplateResponse(request, "import.html", {
        "request": request, "user": user, "slug": slug, "active": slug,
        "title": ent["title"], "fields": ent["fields"], "ket_qua": None,
    })


@app.post("/{slug}/nhap", response_class=HTMLResponse)
async def import_post(slug: str, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    if slug not in ENTITIES:
        return RedirectResponse("/", status_code=303)
    ent = ENTITIES[slug]
    form = await request.form()
    upload = form.get("file")
    ket_qua = {"them": 0, "cap_nhat": 0, "bo_qua": 0, "loi": None}

    if upload is None or not getattr(upload, "filename", ""):
        ket_qua["loi"] = "Chưa chọn file."
    else:
        content = await upload.read()
        records, loi = importer.doc_du_lieu(upload.filename, content, ent["fields"])
        if loi:
            ket_qua["loi"] = loi
        else:
            ket_qua = _upsert_records(db, ent, records)

    return templates.TemplateResponse(request, "import.html", {
        "request": request, "user": user, "slug": slug, "active": slug,
        "title": ent["title"], "fields": ent["fields"], "ket_qua": ket_qua,
    })

