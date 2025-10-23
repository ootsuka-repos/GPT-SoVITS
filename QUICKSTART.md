# クイックスタート - GPT-SoVITS v2ProPlus

## Docker での起動（推奨）

### 1. イメージをビルド
```bash
docker-compose build
```

### 2. コンテナを起動
```bash
docker-compose up -d
```

### 3. WebUI にアクセス
ブラウザで以下にアクセス:
```
http://localhost:9874
```

### 4. コンテナのログを確認
```bash
docker-compose logs -f gpt-sovits
```

### 5. コンテナを停止
```bash
docker-compose down
```

---

## ローカルでの起動

### 1. 環境構築
```bash
conda create -n gpt-sovits python=3.9
conda activate gpt-sovits
pip install -r requirements.txt
```

### 2. WebUI を起動
```bash
python app/webui.py
```

WebUI は自動的に `http://localhost:9874` で起動します。

---

## 推奨システム仕様

- **GPU**: NVIDIA RTX 3090 以上（推奨）
- **メモリ**: 24GB VRAM 推奨、16GB 最小
- **CPU**: 16コア以上推奨
- **ディスク**: 50GB 以上の空き容量

## モデルダウンロード

v2ProPlus の事前学習済みモデルは自動でダウンロードされます。
または、以下から手動でダウンロード可能：

- SoVITS: `GPT_SoVITS/pretrained_models/v2Pro/s2Gv2ProPlus.pth`
- GPT: `GPT_SoVITS/pretrained_models/s1v3.ckpt`
- HuBERT: `GPT_SoVITS/pretrained_models/chinese-hubert-base/`
- RoBERTa: `GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large/`

## よくある質問

### Q: WebUI が起動しない
**A**: ログを確認してください:
```bash
docker-compose logs gpt-sovits
```

### Q: CUDA がない場合
**A**: CPU モードで起動可能ですが、かなり遅くなります:
```bash
docker-compose.yml の `CUDA_VISIBLE_DEVICES` を削除してください
```

### Q: ポートが競合している
**A**: `docker-compose.yml` でポート番号を変更してください:
```yaml
ports:
  - "9875:9874"  # 外部ポート:内部ポート
```

## トラブルシューティング

### メモリ不足
GPU メモリが不足する場合は、`is_half=True` を設定してください（16-bit float を使用）。

### CUDA エラー
```bash
docker-compose exec gpt-sovits nvidia-smi
```
で GPU が認識されているか確認。

## ドキュメント

詳細な設定方法や API 利用方法については、`DOCKER_SETUP.md` を参照してください。

## ライセンス

MIT License
