@echo off
REM ===== Go bo tu khoi dong app MUA HANG (se KHONG tu chay khi dang nhap nua) =====
set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\THNG-MuaHang.lnk"
if exist "%SHORTCUT%" (
  del "%SHORTCUT%"
  echo Da GO tu khoi dong app Mua Hang. Tu lan sau se khong tu chay khi dang nhap.
) else (
  echo Chua cai tu khoi dong (khong tim thay).
)
echo Ban van co the chay tay bang run-mang-noi-bo.bat khi can.
pause
