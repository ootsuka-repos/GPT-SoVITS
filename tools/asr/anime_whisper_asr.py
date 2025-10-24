import argparse
import os
import traceback

import torch
from tqdm import tqdm
from transformers import pipeline

from tools.my_utils import load_cudnn


def execute_asr(input_folder, output_folder, precision):
    """
    Anime Whisperモデルを使用してASRを実行します。

    Args:
        input_folder: 音声ファイルが格納されているフォルダのパス
        output_folder: 文字起こしを保存する出力フォルダ
        precision: モデル計算の精度 (float16, float32)
    """
    print("Anime Whisperモデルを読み込んでいます: litagin/anime-whisper")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if precision == "float16" else torch.float32

    generate_kwargs = {
        "language": "Japanese",
        "no_repeat_ngram_size": 0,
        "repetition_penalty": 1.0,
    }

    pipe = pipeline(
        "automatic-speech-recognition",
        model="litagin/anime-whisper",
        device=device,
        torch_dtype=torch_dtype,
        chunk_length_s=30.0,
    )

    input_file_names = os.listdir(input_folder)
    input_file_names.sort()

    output = []
    output_file_name = os.path.basename(input_folder)

    for file_name in tqdm(input_file_names):
        try:
            file_path = os.path.join(input_folder, file_name)

            # 音声ファイル以外をスキップ
            if not file_name.lower().endswith(('.wav', '.mp3', '.flac', '.m4a', '.ogg')):
                continue

            result = pipe(file_path, generate_kwargs=generate_kwargs)
            text = result["text"].strip()

            # フォーマット: ファイルパス|出力名|言語|テキスト
            output.append(f"{file_path}|{output_file_name}|JA|{text}")

        except Exception as e:
            print(f"{file_name}の処理中にエラーが発生しました: {e}")
            traceback.print_exc()

    output_folder = output_folder or "output/asr_opt"
    os.makedirs(output_folder, exist_ok=True)
    output_file_path = os.path.abspath(f"{output_folder}/{output_file_name}.list")

    with open(output_file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output))
        print(f"ASR処理が完了しました -> 注釈ファイルパス: {output_file_path}\n")

    return output_file_path


load_cudnn()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="日本語音声用Anime Whisper ASR")
    parser.add_argument(
        "-i", "--input_folder", type=str, required=True,
        help="音声ファイルが格納されているフォルダのパス"
    )
    parser.add_argument(
        "-o", "--output_folder", type=str, required=True,
        help="文字起こしを保存する出力フォルダ"
    )
    parser.add_argument(
        "-s", "--model_size", type=str, default="default",
        help="モデルサイズ（anime-whisperでは'default'のみ利用可能）"
    )
    parser.add_argument(
        "-l", "--language", type=str, default="ja",
        help="言語（anime-whisperでは日本語に固定）"
    )
    parser.add_argument(
        "-p", "--precision", type=str, default="float16",
        choices=["float16", "float32"],
        help="モデル計算の精度"
    )

    cmd = parser.parse_args()

    output_file_path = execute_asr(
        input_folder=cmd.input_folder,
        output_folder=cmd.output_folder,
        precision=cmd.precision,
    )
