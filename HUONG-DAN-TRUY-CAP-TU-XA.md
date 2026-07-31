# Truy cập WebApp từ xa (ở nhà / đi công tác) bằng Tailscale

Tailscale tạo một **mạng riêng ảo (VPN)**: khi ở nhà, điện thoại/laptop của chị
"như đang ngồi trong công ty" và mở được WebApp — **an toàn, miễn phí, không lộ ra
internet công cộng, dữ liệu vẫn nằm trên máy văn phòng**.

> Ý tưởng: máy văn phòng (máy chủ) vẫn chạy WebApp như bình thường. Cài Tailscale
> trên **máy chủ** và trên **mỗi thiết bị** cần truy cập từ xa; tất cả dùng **chung
> một tài khoản Tailscale của công ty**. Thế là xong.

---

## Phần 1 — Tạo tài khoản Tailscale (1 lần)

1. Vào **https://tailscale.com** → **Get started / Sign up**.
2. Đăng nhập bằng Google/Microsoft của công ty (nên dùng 1 tài khoản chung cho cả phòng,
   ví dụ email quản trị). Tài khoản này là "chủ" của mạng riêng.

## Phần 2 — Cài trên MÁY CHỦ (máy văn phòng đang chạy WebApp)

1. Tải Tailscale cho Windows: **https://tailscale.com/download** → cài đặt.
2. Mở Tailscale, **đăng nhập bằng đúng tài khoản ở Phần 1**.
3. Sau khi đăng nhập, biểu tượng Tailscale (khay đồng hồ) sẽ hiện **địa chỉ máy** —
   dạng `100.x.x.x` **và** một tên máy (ví dụ `may-kinhdoanh`). Ghi lại địa chỉ này.
4. Đảm bảo WebApp đang chạy bằng **`run-mang-noi-bo.bat`** (bản này mở cho mạng, cần thiết).
   - Nếu Windows hỏi "Allow access" khi chạy, bấm **Allow** (tích cả **Private networks**).

## Phần 3 — Cài trên THIẾT BỊ của nhân viên (laptop, điện thoại)

Làm cho từng thiết bị cần dùng từ xa:

- **Điện thoại:** cài app **Tailscale** từ CH Play / App Store → đăng nhập **cùng
  tài khoản công ty**.
- **Laptop:** tải Tailscale (Windows/macOS) tại **tailscale.com/download** → đăng nhập
  **cùng tài khoản**.

> Mỗi người có thể có tài khoản riêng và được **mời (invite)** vào mạng của công ty
> thay vì dùng chung — xem Phần 6.

## Phần 4 — Truy cập WebApp từ xa

Khi Tailscale đang bật trên thiết bị, mở trình duyệt và gõ (dùng địa chỉ máy chủ ở Phần 2):

- Bằng **tên máy** (dễ nhớ): `http://may-kinhdoanh:8000`
- Hoặc bằng **địa chỉ Tailscale**: `http://100.x.x.x:8000`

Đăng nhập bằng tài khoản WebApp như bình thường. Xong — chị dùng được ở bất cứ đâu
có internet, miễn là Tailscale đang bật.

> 💡 **Bật MagicDNS để dùng tên máy cho tiện:** vào bảng quản trị
> **https://login.tailscale.com/admin/dns** → bật **MagicDNS**. Khi đó gõ tên máy
> (`http://may-kinhdoanh:8000`) là vào được, khỏi nhớ dãy số.

## Phần 5 — Ba việc cần nhớ

| Việc | Chi tiết |
|------|----------|
| **Giữ máy chủ bật + WebApp chạy** | Máy văn phòng phải bật và đang chạy `run-mang-noi-bo.bat` thì mới truy cập từ xa được. |
| **Bật Tailscale trên thiết bị** | Khi ở nhà, mở app Tailscale cho "kết nối" (Connected) rồi mới vào WebApp. |
| **Đổi mật khẩu admin** | Vì giờ vào được từ xa, càng phải đổi mật khẩu admin mặc định (Người dùng → Sửa admin). |

## Phần 6 — Mời nhân viên (giữ an toàn)

- Trong bảng quản trị Tailscale (**https://login.tailscale.com/admin/machines**), chị
  thấy danh sách thiết bị đã kết nối và có thể **mời** thêm người, hoặc **gỡ** thiết bị
  khi nhân viên nghỉ.
- Chỉ thiết bị đã đăng nhập vào mạng Tailscale của công ty mới thấy WebApp — người
  ngoài **không** truy cập được, kể cả biết địa chỉ.

---

## Vì sao cách này an toàn

- WebApp **không mở ra internet công cộng** — không ai ngoài mạng Tailscale của công ty
  chạm tới được.
- Đường truyền giữa các thiết bị được **mã hoá** bởi Tailscale.
- **Dữ liệu vẫn nằm trên máy văn phòng**, không đưa lên cloud.

## Xử lý khi không vào được

1. Thiết bị đã bật Tailscale và ở trạng thái **Connected** chưa?
2. Máy chủ có đang bật và chạy `run-mang-noi-bo.bat` không?
3. Thử địa chỉ IP `http://100.x.x.x:8000` (thay vì tên máy) xem có vào được không —
   nếu có, hãy bật **MagicDNS** (Phần 4).
4. Trên máy chủ, Windows Firewall đã **Allow** cho Python chưa (mạng Private)?
5. Vẫn vướng: chụp màn hình gửi em, em hỗ trợ.

---

*Muốn có địa chỉ web thật (dạng https://baocao-congty.com) để vào bằng trình duyệt
bất kỳ mà không cài gì — báo em, mình sẽ cân nhắc phương án Cloudflare Tunnel (cần
tên miền + IT hỗ trợ).*
