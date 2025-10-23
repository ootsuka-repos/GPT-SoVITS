#!/bin/bash
set -e

echo "GPT-SoVITS v2ProPlus Docker Container Starting..."
echo "================================================"

# Setup symbolic links for models
echo "Setting up model directories..."
rm -rf /workspace/GPT-SoVITS/GPT_SoVITS/pretrained_models 2>/dev/null || true
rm -rf /workspace/GPT-SoVITS/GPT_SoVITS/text/G2PWModel 2>/dev/null || true
rm -rf /workspace/GPT-SoVITS/tools/asr/models 2>/dev/null || true
rm -rf /workspace/GPT-SoVITS/tools/uvr5/uvr5_weights 2>/dev/null || true

mkdir -p /workspace/models

ln -sf /workspace/models/pretrained_models /workspace/GPT-SoVITS/GPT_SoVITS/pretrained_models
ln -sf /workspace/models/G2PWModel /workspace/GPT-SoVITS/GPT_SoVITS/text/G2PWModel
ln -sf /workspace/models/asr_models /workspace/GPT-SoVITS/tools/asr/models
ln -sf /workspace/models/uvr5_weights /workspace/GPT-SoVITS/tools/uvr5/uvr5_weights

echo "Model directories configured"
echo ""
echo "Starting WebUI on port 9874..."
echo "Access the WebUI at: http://localhost:9874"
echo "================================================"

# Activate conda and start WebUI
exec bash -c "source /opt/miniconda3/etc/profile.d/conda.sh && conda activate base && python app/webui.py"
