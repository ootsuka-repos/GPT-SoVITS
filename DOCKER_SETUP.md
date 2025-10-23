# Docker セットアップガイド - GPT-SoVITS v2ProPlus

## 概要
GPT-SoVITS v2ProPlus をDocker コンテナで実行し、WebUI をポート経由で公開します。

## 必要要件
- Docker Desktop (または Docker Engine)
- NVIDIA GPU (推奨)
- nvidia-docker (GPU サポート用)
- 10GB 以上のディスク容量

## クイックスタート

### 1. Docker イメージのビルド
```bash
docker-compose build
```

### 2. Docker コンテナの起動
```bash
docker-compose up -d
```

### 3. WebUI へのアクセス
ブラウザで以下にアクセス：
- **メイン WebUI**: http://localhost:9874
- **TTS 推理 WebUI**: http://localhost:9872
- **音声標注 WebUI**: http://localhost:9871
- **人声分離 WebUI**: http://localhost:9873
- **API**: http://localhost:9880

## 詳細設定

### コンテナログの確認
```bash
docker-compose logs -f gpt-sovits
```

### コンテナの停止
```bash
docker-compose down
```

### ボリューム（永続データ）
以下のディレクトリがホストマシンに永続化されます：
- `./logs/` - トレーニングログ
- `./output/` - 推理出力
- `./SoVITS_weights_v2ProPlus/` - v2ProPlus SoVITS モデル
- `./GPT_weights_v2ProPlus/` - v2ProPlus GPT モデル
- `models/` - 事前学習済みモデル（初回起動時に自動作成）

### 環境変数

`docker-compose.yml` で以下の環境変数を設定できます：

- `CUDA_VISIBLE_DEVICES`: 使用する GPU ID (デフォルト: 0)
- `is_half`: 16-bit float を使用 (True/False、デフォルト: True)
- `is_share`: Gradio 共有リンクを生成 (True/False、デフォルト: True)
- `language`: UI言語 (デフォルト: ja_JP)

## モデルファイルの準備

### 事前学習済みモデルの配置
以下の構造で `models/` ディレクトリにモデルを配置してください：

```
models/
├── pretrained_models/
│   ├── v2Pro/
│   │   └── s2Gv2ProPlus.pth
│   ├── s1v3.ckpt
│   ├── chinese-hubert-base/
│   ├── chinese-roberta-wwm-ext-large/
│   └── G2PWModel/
├── asr_models/
└── uvr5_weights/
```

## トラブルシューティング

### CUDA エラー
```bash
# GPU が認識されているか確認
docker-compose exec gpt-sovits nvidia-smi
```

### ポート競合エラー
ポート 9874 が既に使用されている場合、`docker-compose.yml` で `9874:9874` を `9875:9874` など別のポートに変更してください。

### メモリ不足
`docker-compose.yml` の `deploy.resources` セクションでメモリ制限を調整してください。

## パフォーマンス最適化

### GPU メモリ設定
大規模なモデルの場合、環境変数で半精度を有効にしてください：
```yaml
environment:
  - is_half=True
```

### マルチ GPU 使用
```yaml
environment:
  - CUDA_VISIBLE_DEVICES=0,1,2,3
```

## ネットワークアクセス

### リモートからアクセス
デフォルトでは `localhost` からのみアクセス可能です。リモートからアクセスする場合：

1. ファイアウォール設定を確認
2. ポートを外部に公開（セキュリティ注意）
3. リバースプロキシ（nginx 等）を使用

## API 利用

WebUI の代わりに API を直接利用できます：

```bash
curl -X POST http://localhost:9880 \
  -H "Content-Type: application/json" \
  -d '{"text": "こんにちは", "text_language": "ja"}'
```

## ライセンス
このプロジェクトは MIT ライセンスの下で公開されています。
