#!/bin/bash

# GPT-SoVITS Docker 起動スクリプト

echo "========================================"
echo "GPT-SoVITS Docker起動"
echo "========================================"

# モデルディレクトリの作成
mkdir -p logs output
mkdir -p SoVITS_weights SoVITS_weights_v2 SoVITS_weights_v3 SoVITS_weights_v4
mkdir -p SoVITS_weights_v2Pro SoVITS_weights_v2ProPlus
mkdir -p GPT_weights GPT_weights_v2 GPT_weights_v3 GPT_weights_v4
mkdir -p GPT_weights_v2Pro GPT_weights_v2ProPlus

# Docker Composeでビルドと起動
echo "Dockerイメージをビルド中..."
docker-compose build

echo "コンテナを起動中..."
docker-compose up -d

echo ""
echo "========================================"
echo "GPT-SoVITS Web UIが起動しました！"
echo "========================================"
echo ""
echo "以下のURLでアクセスできます："
echo "  メインWebUI:     http://localhost:9874"
echo "  TTS推理WebUI:    http://localhost:9872"
echo "  人声分離WebUI:   http://localhost:9873"
echo "  音声標注WebUI:   http://localhost:9871"
echo "  API:             http://localhost:9880"
echo ""
echo "ログを確認: docker-compose logs -f"
echo "停止: docker-compose down"
echo "========================================"
