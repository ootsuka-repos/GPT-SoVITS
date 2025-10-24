# Tech Stack
- **Language**: Python 3.11 (per Dockerfile), CUDA-enabled for GPU workflows.
- **Core Libraries**: PyTorch/torchaudio, PyTorch Lightning, transformers, peft, rotary_embedding_torch, sentencepiece.
- **Inference / Serving**: Gradio WebUI, FastAPI (with Uvicorn via `fastapi[standard]`), huggingface_hub for model assets, BigVGAN vocoder integration.
- **NLP / Linguistics**: jieba, g2p_en, g2pk2, ko_pron, OpenCC, ToJyutping, fast_langdetect, wordsegment.
- **Audio Utils**: librosa, ctranslate2, funasr, ffmpeg-python, av, denoising and slicer tools under `tools/`.
- **Environment**: Docker image based on `nvidia/cuda:12.6.0-cudnn-devel-ubuntu22.04`; CUDA devices passed via compose; targeted for Darwin host with GPU passthrough.
- **Optional Assets**: Pretrained models downloaded via huggingface_hub; external dependencies include pyopenjtalk (installed from git).