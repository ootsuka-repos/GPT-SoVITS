@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo GPT-SoVITS Docker起動
echo ========================================
echo.

REM モデルディレクトリの作成
if not exist "logs" mkdir logs
if not exist "output" mkdir output
if not exist "SoVITS_weights" mkdir SoVITS_weights
if not exist "SoVITS_weights_v2" mkdir SoVITS_weights_v2
if not exist "SoVITS_weights_v3" mkdir SoVITS_weights_v3
if not exist "SoVITS_weights_v4" mkdir SoVITS_weights_v4
if not exist "SoVITS_weights_v2Pro" mkdir SoVITS_weights_v2Pro
if not exist "SoVITS_weights_v2ProPlus" mkdir SoVITS_weights_v2ProPlus
if not exist "GPT_weights" mkdir GPT_weights
if not exist "GPT_weights_v2" mkdir GPT_weights_v2
if not exist "GPT_weights_v3" mkdir GPT_weights_v3
if not exist "GPT_weights_v4" mkdir GPT_weights_v4
if not exist "GPT_weights_v2Pro" mkdir GPT_weights_v2Pro
if not exist "GPT_weights_v2ProPlus" mkdir GPT_weights_v2ProPlus

REM Docker Composeでビルドと起動
echo Dockerイメージをビルド中...
docker-compose build

echo コンテナを起動中...
docker-compose up -d

echo.
echo ========================================
echo GPT-SoVITS Web UIが起動しました！
echo ========================================
echo.
echo 以下のURLでアクセスできます：
echo   メインWebUI:     http://localhost:9874
echo   TTS推理WebUI:    http://localhost:9872
echo   人声分離WebUI:   http://localhost:9873
echo   音声標注WebUI:   http://localhost:9871
echo   API:             http://localhost:9880
echo.
echo ログを確認: docker-compose logs -f
echo 停止: docker-compose down
echo ========================================
echo.

pause
