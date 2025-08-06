@echo off
echo Building Tetris Windows...

REM 確保安裝了 pyinstaller
pip install pyinstaller

REM 清理舊的建置檔案
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "TetrisWindows.exe" del "TetrisWindows.exe"

REM 建置遊戲
pyinstaller tetris_windows.spec

REM 檢查是否建置成功
if exist "dist\TetrisWindows.exe" (
    echo.
    echo ✅ Build successful! 
    echo 📁 Executable location: dist\TetrisWindows.exe
    echo.
    echo 🎮 Starting Tetris Windows...
    start "" "dist\TetrisWindows.exe"
) else (
    echo.
    echo ❌ Build failed!
    echo Please check the error messages above.
)

pause
