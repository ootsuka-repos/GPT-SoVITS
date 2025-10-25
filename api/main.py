"""FastAPI server for GPT-SoVITS v2ProPlus inference."""

from __future__ import annotations

import asyncio
import base64
import io
import os
import tempfile
import wave
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import torch
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from GPT_SoVITS.TTS_infer_pack.TTS import TTS, TTS_Config


# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------

os.environ.setdefault("version", "v2ProPlus")

app = FastAPI(title="GPT-SoVITS v2ProPlus API", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_pipeline_lock = asyncio.Lock()
_tts_pipeline: Optional[TTS] = None

TEXT_SPLIT_METHODS = {"none": "cut0", "sentences": "cut1", "balanced": "cut2", "zh_punctuation": "cut3", "en_punctuation": "cut4", "all_punctuation": "cut5"}


class SynthesisRequest(BaseModel):
    text: str = Field(..., description="Target text to be synthesized.")
    reference_audio: Optional[str] = Field(None, description="Base64-encoded reference audio (mono WAV recommended).")
    reference_audio_path: Optional[str] = Field(None, description="Path to reference audio file.")
    gpt_model_path: Optional[str] = Field(None, description="Path to GPT model file (.ckpt)")
    sovits_model_path: Optional[str] = Field(None, description="Path to SoVITS model file (.pth)")
    text_language: str = Field("auto", description="Language of the target text (e.g. auto, zh, en, ja, yue, ko, all_zh, all_ja, all_yue, all_ko, auto_yue).")
    prompt_text: Optional[str] = Field(None, description="Transcript of the reference audio. Leave empty if unknown.")
    prompt_language: str = Field("zh", description="Language code for the prompt text.")
    auxiliary_reference_audios: Optional[List[str]] = Field(None, description="Optional list of additional base64-encoded reference audios for tone fusion.")
    top_k: int = Field(20, ge=1, le=100, description="Sampling top_k for the GPT decoder.")
    top_p: float = Field(0.6, ge=0.0, le=1.0, description="Sampling top_p for the GPT decoder.")
    temperature: float = Field(0.6, ge=0.0, le=1.0, description="Sampling temperature for the GPT decoder.")
    text_split_method: str = Field("none", description=f"Text split heuristic. Options: {', '.join(TEXT_SPLIT_METHODS.keys())}.")
    batch_size: int = Field(1, ge=1, le=4, description="Batch size for decoding segments.")
    batch_threshold: float = Field(0.75, ge=0.1, le=1.5, description="Bucket threshold for batching segments.")
    speed: float = Field(1.0, ge=0.3, le=2.0, description="Playback speed factor.")
    pause: float = Field(0.3, ge=0.0, le=1.0, description="Pause length (seconds) appended between segments.")
    seed: int = Field(-1, description="Random seed. Use -1 for random seed per request.")
    parallel_infer: Optional[bool] = Field(None, description="Override for parallel inference. Defaults to GPU availability.")
    repetition_penalty: float = Field(1.35, ge=0.5, le=2.5, description="Repetition penalty for GPT decoder.")
    sample_steps: int = Field(32, ge=4, le=128, description="Diffusion sample steps for vocoder when applicable.")


class SynthesisResponse(BaseModel):
    sample_rate: int
    audio_base64: str
    duration_seconds: float


class MetadataResponse(BaseModel):
    version: str
    device: str
    is_half: bool
    text_languages: List[str]
    prompt_languages: List[str]
    text_split_methods: List[str]


class LoadModelsRequest(BaseModel):
    gpt_model_path: str = Field(..., description="Path to GPT model file (.ckpt)")
    sovits_model_path: str = Field(..., description="Path to SoVITS model file (.pth)")


class LoadModelsResponse(BaseModel):
    success: bool
    message: str


def _ensure_tts_pipeline(gpt_path: Optional[str] = None, sovits_path: Optional[str] = None) -> TTS:
    global _tts_pipeline

    # If paths are provided, force reload
    if gpt_path is not None and sovits_path is not None:
        _tts_pipeline = None

    if _tts_pipeline is not None:
        return _tts_pipeline

    # Get model paths from parameters or environment variables
    gpt_model_path = gpt_path or os.environ.get("GPT_MODEL_PATH", "")
    sovits_model_path = sovits_path or os.environ.get("SOVITS_MODEL_PATH", "")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Create config with model paths
    config = {
        "custom": {
            "device": device,
            "is_half": device == "cuda",
            "version": "v2ProPlus",
            "t2s_weights_path": gpt_model_path,
            "vits_weights_path": sovits_model_path,
            "cnhuhbert_base_path": "GPT_SoVITS/pretrained_models/chinese-hubert-base",
            "bert_base_path": "GPT_SoVITS/pretrained_models/chinese-roberta-wwm-ext-large",
        }
    }

    cfg = TTS_Config(config)
    pipeline = TTS(cfg)
    _tts_pipeline = pipeline
    return pipeline


async def _synthesize(inputs: Dict) -> SynthesisResponse:
    async with _pipeline_lock:
        pipeline = _ensure_tts_pipeline()

        def _run() -> SynthesisResponse:
            result = None
            for sr, audio in pipeline.run(inputs):
                result = (sr, audio)
            if result is None:
                raise RuntimeError("No audio generated.")
            sample_rate, audio = result
            if isinstance(audio, torch.Tensor):
                audio = audio.detach().cpu().numpy()
            audio = np.asarray(audio, dtype=np.int16)
            if audio.ndim > 1:
                audio = audio.reshape(-1)
            buffer = io.BytesIO()
            with wave.open(buffer, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(audio.tobytes())
            buffer.seek(0)
            audio_b64 = base64.b64encode(buffer.read()).decode("ascii")
            duration = float(audio.shape[0]) / float(sample_rate)
            return SynthesisResponse(sample_rate=sample_rate, audio_base64=audio_b64, duration_seconds=duration)

        return await asyncio.to_thread(_run)


def _write_temp_audio(data: bytes, suffix: str) -> str:
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(data)
    tmp.flush()
    tmp.close()
    return tmp.name


def _decode_base64_audio(encoded: str) -> bytes:
    try:
        return base64.b64decode(encoded, validate=True)
    except (base64.binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid base64 audio payload.") from exc


@app.on_event("startup")
async def _load_on_startup() -> None:
    # モデルは/load_modelsエンドポイントで明示的にロードする
    # 環境変数が設定されている場合のみ自動ロード
    gpt_path = os.environ.get("GPT_MODEL_PATH", "")
    sovits_path = os.environ.get("SOVITS_MODEL_PATH", "")
    if gpt_path and sovits_path:
        await asyncio.to_thread(_ensure_tts_pipeline)


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/metadata", response_model=MetadataResponse)
async def metadata() -> MetadataResponse:
    pipeline = _ensure_tts_pipeline()
    config = pipeline.configs
    return MetadataResponse(
        version="v2ProPlus",
        device=str(config.device),
        is_half=bool(config.is_half),
        text_languages=list(config.v2_languages),
        prompt_languages=list(config.v2_languages),
        text_split_methods=list(TEXT_SPLIT_METHODS.keys()),
    )


@app.post("/load_models", response_model=LoadModelsResponse)
async def load_models(request: LoadModelsRequest) -> LoadModelsResponse:
    """Load or reload GPT and SoVITS models with specified paths."""
    global _tts_pipeline

    try:
        # Validate paths
        if not Path(request.gpt_model_path).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"GPT model file not found: {request.gpt_model_path}"
            )

        if not Path(request.sovits_model_path).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"SoVITS model file not found: {request.sovits_model_path}"
            )

        async with _pipeline_lock:
            # Clear existing pipeline
            _tts_pipeline = None

            # Load new models
            await asyncio.to_thread(
                _ensure_tts_pipeline,
                request.gpt_model_path,
                request.sovits_model_path
            )

        return LoadModelsResponse(
            success=True,
            message=f"Models loaded successfully: GPT={request.gpt_model_path}, SoVITS={request.sovits_model_path}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load models: {str(e)}"
        )


@app.post("/tts", response_model=SynthesisResponse)
async def tts(request: SynthesisRequest) -> SynthesisResponse:
    # モデルパスが指定されている場合はロード
    if request.gpt_model_path and request.sovits_model_path:
        pipeline = _ensure_tts_pipeline(request.gpt_model_path, request.sovits_model_path)
    else:
        pipeline = _ensure_tts_pipeline()

    valid_languages = set(pipeline.configs.v2_languages)

    if request.text_language not in valid_languages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported text_language '{request.text_language}'. Valid options: {sorted(valid_languages)}",
        )
    if request.prompt_language not in valid_languages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported prompt_language '{request.prompt_language}'. Valid options: {sorted(valid_languages)}",
        )

    if request.text_split_method not in TEXT_SPLIT_METHODS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported text_split_method '{request.text_split_method}'. Options: {list(TEXT_SPLIT_METHODS.keys())}",
        )

    # リファレンス音声の処理
    ref_path_to_delete = None
    if request.reference_audio_path:
        # ファイルパスが指定されている場合
        ref_path = request.reference_audio_path
        if not Path(ref_path).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Reference audio file not found: {ref_path}"
            )
    elif request.reference_audio:
        # Base64エンコードされた音声データの場合
        ref_bytes = _decode_base64_audio(request.reference_audio)
        ref_suffix = ".wav"
        ref_path = _write_temp_audio(ref_bytes, ref_suffix)
        ref_path_to_delete = ref_path
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either reference_audio or reference_audio_path must be provided"
        )

    aux_paths: List[str] = []
    try:
        if request.auxiliary_reference_audios:
            for encoded in request.auxiliary_reference_audios:
                aux_bytes = _decode_base64_audio(encoded)
                aux_paths.append(_write_temp_audio(aux_bytes, ref_suffix))

        inputs = {
            "text": request.text,
            "text_lang": request.text_language,
            "ref_audio_path": ref_path,
            "aux_ref_audio_paths": aux_paths,
            "prompt_text": request.prompt_text or "",
            "prompt_lang": request.prompt_language,
            "top_k": request.top_k,
            "top_p": request.top_p,
            "temperature": request.temperature,
            "text_split_method": TEXT_SPLIT_METHODS[request.text_split_method],
            "batch_size": request.batch_size,
            "batch_threshold": request.batch_threshold,
            "speed_factor": request.speed,
            "split_bucket": True,
            "fragment_interval": request.pause,
            "seed": request.seed,
            "parallel_infer": request.parallel_infer if request.parallel_infer is not None else torch.cuda.is_available(),
            "repetition_penalty": request.repetition_penalty,
            "sample_steps": request.sample_steps,
            "return_fragment": False,
        }

        return await _synthesize(inputs)
    finally:
        if ref_path_to_delete:
            Path(ref_path_to_delete).unlink(missing_ok=True)
        for path in aux_paths:
            Path(path).unlink(missing_ok=True)
