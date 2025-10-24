@echo off
chcp 65001 >nul
echo ====================================
echo GPT-SoVITS WebUI + API 同時起動
echo ====================================
echo.

REM 仮想環境の存在確認
if not exist .venv (
    echo [エラー] 仮想環境が見つかりません
    echo まず setup_venv.bat を実行してセットアップしてください
    pause
    exit /b 1
)

echo WebUIとAPIサーバーを別ウィンドウで起動します...
echo.

REM WebUIを新しいウィンドウで起動
start cmd /k "title GPT-SoVITS-WebUI & call .venv\Scripts\activate.bat & echo WebUI起動中... (http://localhost:9874) & python app\webui.py"

REM 3秒待機
timeout /t 3 /nobreak >nul

REM APIサーバーを新しいウィンドウで起動
start cmd /k "title GPT-SoVITS-API & call .venv\Scripts\activate.bat & echo APIサーバー起動中... (http://localhost:9880) & uvicorn api.main:app --host 0.0.0.0 --port 9880"

echo.
echo ====================================
echo 起動しました！
echo WebUI: http://localhost:9874
echo API: http://localhost:9880
echo ====================================
echo.
echo 各ウィンドウを閉じるか、Ctrl+Cで終了できます
echo.
pause
