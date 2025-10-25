@echo off
chcp 65001 >nul
echo ====================================
echo GPT-SoVITS WebUI 起動
echo ====================================
echo.

REM 仮想環境の存在確認
if not exist .venv (
    echo [エラー] 仮想環境が見つかりません
    echo まず setup_venv.bat を実行してセットアップしてください
    pause
    exit /b 1
)

echo WebUIを起動しています...
echo URL: http://localhost:9874
echo.
echo 終了するにはCtrl+Cを押してください
echo ====================================
echo.

REM FFmpegの共有ライブラリをPATHに追加
set "PATH=%~dp0ffmpeg\ffmpeg-n7.1-latest-win64-lgpl-shared-7.1\bin;%PATH%"

call .venv\Scripts\activate.bat
python app\webui.py
