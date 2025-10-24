#!/usr/bin/env python3
"""Download GPT-SoVITS pretrained assets from Hugging Face."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Iterable, Set

try:
    from huggingface_hub import hf_hub_download, list_repo_files
    from huggingface_hub.utils import HfHubHTTPError
except ImportError:  # pragma: no cover - handled at runtime
    print("huggingface_hub is required. Install with `pip install huggingface_hub`.", file=sys.stderr)
    sys.exit(1)


REPO_ROOT = Path(__file__).resolve().parent.parent
PRETRAINED_ROOT = REPO_ROOT / "GPT_SoVITS" / "pretrained_models"

SNAPSHOT_REPOS = {
    "chinese-roberta-wwm-ext-large": "hfl/chinese-roberta-wwm-ext-large",
    "chinese-hubert-base": "TencentGameMate/chinese-hubert-base",
    "models--nvidia--bigvgan_v2_24khz_100band_256x": "nvidia/bigvgan_v2_24khz_100band_256x",
}

SV_MODEL = "GPT_SoVITS/pretrained_models/sv/pretrained_eres2netv2w24s4ep4.ckpt"

SUPPORTED_VERSION = "v2ProPlus"
VERSION_REQUIREMENTS = {
    SUPPORTED_VERSION: {
        "GPT_SoVITS/pretrained_models/s1v3.ckpt",
        "GPT_SoVITS/pretrained_models/v2Pro/s2Gv2ProPlus.pth",
    }
}

VERSION_ALIASES = {
    "all": SUPPORTED_VERSION,
    "v2proplus": SUPPORTED_VERSION,
}


def parse_versions(raw: str) -> Set[str]:
    value = raw.strip().lower()
    if value in {"all", ""}:
        return set(VERSION_REQUIREMENTS.keys())
    selected: Set[str] = set()
    for token in value.split(","):
        key = token.strip().lower()
        if not key:
            continue
        if key not in VERSION_ALIASES:
            available = ", ".join(sorted(VERSION_ALIASES))
            raise argparse.ArgumentTypeError(f"Unknown version '{token}'. Choose from: {available}")
        selected.add(VERSION_ALIASES[key])
    return selected


def download_repo_snapshot(repo_id: str, destination: Path, *, token: str | None, force: bool) -> None:
    """Download every file from a Hugging Face repo into destination."""

    if destination.exists() and any(destination.iterdir()) and not force:
        rel = destination.relative_to(REPO_ROOT)
        print(f"✓ {rel} already present")
        return

    print(f"→ Syncing snapshot {repo_id} -> {destination.relative_to(REPO_ROOT)}")
    destination.mkdir(parents=True, exist_ok=True)
    try:
        repo_files = list_repo_files(repo_id=repo_id, repo_type="model", token=token)
    except HfHubHTTPError as exc:
        raise SystemExit(f"Failed to list files for {repo_id}: {exc}")

    for repo_file in repo_files:
        local_file = destination / repo_file
        if local_file.exists() and not force:
            continue
        local_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            hf_hub_download(
                repo_id=repo_id,
                filename=repo_file,
                token=token,
                local_dir=str(destination),
                local_dir_use_symlinks=False,
                force_download=force,
            )
        except HfHubHTTPError as exc:
            raise SystemExit(f"Failed to download {repo_id}:{repo_file}: {exc}")


def download_weight_file(relative_path: str, *, token: str | None, force: bool) -> None:
    """Fetch a single file from lj1995/GPT-SoVITS into the repo tree."""

    repo_id = "lj1995/GPT-SoVITS"
    target = REPO_ROOT / relative_path
    if target.exists() and not force:
        print(f"✓ {relative_path} already present")
        return

    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"→ Downloading {relative_path}")
    try:
        hf_hub_download(
            repo_id=repo_id,
            filename=relative_path,
            token=token,
            local_dir=str(REPO_ROOT),
            local_dir_use_symlinks=False,
            force_download=force,
        )
    except HfHubHTTPError as exc:
        raise SystemExit(f"Failed to download {relative_path} from {repo_id}: {exc}")


def gather_required_files(versions: Iterable[str], include_sv: bool) -> Set[str]:
    required: Set[str] = set()
    for version in versions:
        required.update(VERSION_REQUIREMENTS.get(version, set()))
    if include_sv:
        required.add(SV_MODEL)
    return required


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--versions",
        default="all",
        help="Comma separated versions to prepare (only 'v2ProPlus' or 'all').",
    )
    parser.add_argument(
        "--mirror",
        help="Optional Hugging Face mirror endpoint, e.g. https://hf-mirror.com",
    )
    parser.add_argument("--token", help="Hugging Face access token if required.")
    parser.add_argument("--skip-sv", action="store_true", help="Skip speaker verification checkpoint download.")
    parser.add_argument("--skip-bigvgan", action="store_true", help="Skip BigVGAN vocoder snapshot download.")
    parser.add_argument("--list-only", action="store_true", help="Only list assets without downloading.")
    parser.add_argument("--force", action="store_true", help="Force re-download even if files exist.")

    args = parser.parse_args()

    if args.mirror:
        os.environ["HF_ENDPOINT"] = args.mirror.rstrip("/")

    try:
        versions = parse_versions(args.versions)
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))

    required_files = gather_required_files(versions, include_sv=not args.skip_sv)

    print("Selected versions:", ", ".join(sorted(versions)) or "(none)")
    if args.list_only:
        if required_files:
            print("Weights:")
            for path in sorted(required_files):
                print("  -", path)
        snapshots = dict(SNAPSHOT_REPOS)
        if args.skip_bigvgan:
            snapshots = {k: v for k, v in snapshots.items() if k != "models--nvidia--bigvgan_v2_24khz_100band_256x"}
        if snapshots:
            print("Model snapshots:")
            for name, repo_id in snapshots.items():
                print(f"  - {name} <- {repo_id}")
        return

    PRETRAINED_ROOT.mkdir(parents=True, exist_ok=True)

    snapshots = dict(SNAPSHOT_REPOS)
    if args.skip_bigvgan:
        snapshots.pop("models--nvidia--bigvgan_v2_24khz_100band_256x", None)

    for name, repo_id in snapshots.items():
        destination = PRETRAINED_ROOT / name
        download_repo_snapshot(repo_id, destination, token=args.token, force=args.force)

    for relative_path in sorted(required_files):
        download_weight_file(relative_path, token=args.token, force=args.force)

    print("Done. Pretrained assets are stored under GPT_SoVITS/pretrained_models/.")


if __name__ == "__main__":
    main()
