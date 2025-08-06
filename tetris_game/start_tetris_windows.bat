@echo off
echo Starting Tetris Windows...

REM 檢查是否存在可執行檔
if exist "dist\TetrisWindows.exe" (
    echo 🎮 Launching Tetris Windows...
    start "" "dist\TetrisWindows.exe"
) else if exist "TetrisWindows.exe" (
    echo 🎮 Launching Tetris Windows...
    start "" "TetrisWindows.exe"
) else (
    echo ❌ TetrisWindows.exe not found!
    echo Please build the game first using build_tetris_windows.bat
    echo.
    echo 🔧 Running from source instead...
    python main.py
)

pause
