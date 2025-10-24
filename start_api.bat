@echo off
chcp 65001 >nul
echo ====================================
echo GPT-SoVITS API サーバー起動
echo ====================================
echo.

REM 仮想環境の存在確認
if not exist .venv (
    echo [エラー] 仮想環境が見つかりません
    echo まず setup_venv.bat を実行してセットアップしてください
    pause
    exit /b 1
)

echo APIサーバーを起動しています...
echo URL: http://localhost:9880
echo.
echo 終了するにはCtrl+Cを押してください
echo ====================================
echo.

call .venv\Scripts\activate.bat
uvicorn api.main:app --host 0.0.0.0 --port 9880
