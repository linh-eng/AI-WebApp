@echo off
REM ===== Cai dat: WebApp Kinh Doanh TU KHOI DONG khi dang nhap Windows =====
REM Bam dup file nay MOT LAN. Tu lan sau, moi khi bat may va dang nhap,
REM WebApp se tu chay (cua so thu nho o thanh tac vu).
cd /d "%~dp0"

set "TARGET=%~dp0run-mang-noi-bo.bat"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT=%STARTUP%\THNG-KinhDoanh.lnk"

if not exist "%TARGET%" (
  echo Khong tim thay run-mang-noi-bo.bat trong thu muc nay. Dung file nay trong thu muc app.
  pause & exit /b 1
)

powershell -NoProfile -Command "$w=New-Object -ComObject WScript.Shell; $s=$w.CreateShortcut('%SHORTCUT%'); $s.TargetPath='%TARGET%'; $s.WorkingDirectory='%~dp0'; $s.WindowStyle=7; $s.Description='THNG - Bao cao Kinh doanh'; $s.Save()"

echo.
echo ================================================================
echo   DA CAI DAT TU KHOI DONG.
echo   Tu lan sau, WebApp se tu chay khi ban dang nhap Windows.
echo   (Cua so chay se thu nho duoi thanh tac vu - dung dong no.)
echo.
echo   Muon TAT tu khoi dong: chay  tat-tu-khoi-dong.bat
echo   * Ghi may chu phai luon BAT va dang nhap thi ca phong moi vao duoc.
echo ================================================================
echo.
pause
