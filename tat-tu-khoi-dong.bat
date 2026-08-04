@echo off
REM ===== Go bo tu khoi dong (WebApp se KHONG tu chay khi dang nhap nua) =====
set "SHORTCUT=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\THNG-KinhDoanh.lnk"
if exist "%SHORTCUT%" (
  del "%SHORTCUT%"
  echo Da GO tu khoi dong. Tu lan sau WebApp se khong tu chay khi dang nhap.
) else (
  echo Chua cai tu khoi dong (khong tim thay).
)
echo Ban van co the chay tay bang run-mang-noi-bo.bat khi can.
pause
