@echo off
chcp 65001 >nul
echo ====================================
echo 仮想環境セットアップスクリプト
echo GPT-SoVITS v2ProPlus
echo ====================================
echo.

REM Pythonのバージョンを確認
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [エラー] Pythonが見つかりません
    echo Python 3.10以上をインストールしてください
    pause
    exit /b 1
)

echo [1/5] Pythonバージョンを確認中...
python --version

echo.
echo [2/5] 仮想環境を作成中...
if exist .venv (
    echo 既存の.venvフォルダが見つかりました
    choice /c YN /m "削除して再作成しますか？"
    if errorlevel 2 goto skip_venv_creation
    if errorlevel 1 (
        echo 既存の.venvを削除中...
        rmdir /s /q .venv
    )
)

python -m venv .venv
if %errorlevel% neq 0 (
    echo [エラー] 仮想環境の作成に失敗しました
    pause
    exit /b 1
)
echo 仮想環境を作成しました

:skip_venv_creation

echo.
echo [3/5] 仮想環境をアクティベート中...
call .venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [エラー] 仮想環境のアクティベートに失敗しました
    pause
    exit /b 1
)

echo.
echo [4/5] pipをアップグレード中...
python -m pip install --upgrade pip

echo.
echo [5/5] 依存関係をインストール中...
echo これには数分かかる場合があります...
echo.

echo PyTorchをインストール中 (CUDA 12.6)...
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu126
if %errorlevel% neq 0 (
    echo [エラー] PyTorchのインストールに失敗しました
    pause
    exit /b 1
)

echo.
echo torchcodecをインストール中...
pip install torchcodec
if %errorlevel% neq 0 (
    echo [警告] torchcodecのインストールに失敗しました（継続します）
)

echo.
echo その他の依存関係をインストール中...
pip install Cython
pip install git+https://github.com/r9y9/pyopenjtalk.git@v0.4.1

REM requirements.txtからpyopenjtalkを除外してインストール
findstr /v /i "pyopenjtalk" requirements.txt > temp_requirements.txt
pip install -r temp_requirements.txt
del temp_requirements.txt

if %errorlevel% neq 0 (
    echo [エラー] 依存関係のインストールに失敗しました
    pause
    exit /b 1
)

echo.
echo ====================================
echo セットアップが完了しました！
echo ====================================
echo.
echo 次のステップ:
echo 1. start_webui.bat を実行してWebUIを起動
echo 2. start_api.bat を実行してAPIサーバーを起動
echo.
pause
