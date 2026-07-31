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

from . import calculations, excel_export, models, web_meta
from .config import BASE_DIR, SECRET_KEY
from .database import Base, engine, get_db
from .security import verify_password
from .seed import khoi_tao_du_lieu

app = FastAPI(title="WebApp Báo cáo Kinh doanh THNG")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY, max_age=8 * 3600)
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@app.on_event("startup")
def _startup():
    Base.metadata.create_all(bind=engine)
    khoi_tao_du_lieu()


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

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    tq = calculations.tong_quan(
        db.scalars(select(models.KhachHang)).all(),
        db.scalars(select(models.BaoGia)).all(),
        db.scalars(select(models.HopDong)).all(),
        db.scalars(select(models.ThanhToan)).all(),
    )
    return templates.TemplateResponse(request, "dashboard.html", {"request": request, "user": user, "tq": tq, "active": "dashboard"}
    )


# ---- Xuất báo cáo Excel -------------------------------------------------

@app.get("/xuat-excel")
def xuat_excel(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    data = excel_export.xuat_bao_cao(
        db.scalars(select(models.KhachHang)).all(),
        db.scalars(select(models.BaoGia)).all(),
        db.scalars(select(models.HopDong)).all(),
        db.scalars(select(models.ThanhToan)).all(),
    )
    ten = f"Bao_cao_kinh_doanh_THNG_{date.today():%Y%m%d}.xlsx"
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{ten}"'},
    )


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
}


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


@app.get("/{slug}", response_class=HTMLResponse)
def list_view(slug: str, request: Request, db: Session = Depends(get_db)):
    if slug not in ENTITIES:
        return _redirect_login() if slug != "favicon.ico" else Response(status_code=404)
    user = current_user(request, db)
    if not user:
        return _redirect_login()
    ent = ENTITIES[slug]
    records = db.scalars(select(ent["model"])).all()
    fields = ent["fields"]
    rows = []
    for rec in records:
        cells = [_display_value(f, getattr(rec, f["name"])) for f in fields]
        rows.append({"pk": getattr(rec, ent["pk"]), "cells": cells})
    return templates.TemplateResponse(request, "list.html", {
        "request": request, "user": user, "slug": slug, "active": slug,
        "title": ent["title"], "headers": [f["label"] for f in fields], "rows": rows,
    })


@app.get("/{slug}/them", response_class=HTMLResponse)
def new_form(slug: str, request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return _redirect_login()
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
    ent = ENTITIES[slug]
    obj = db.scalar(select(ent["model"]).where(getattr(ent["model"], ent["pk"]) == pk))
    if obj:
        db.delete(obj)
        db.commit()
    return RedirectResponse(f"/{slug}", status_code=303)
