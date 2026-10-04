"""Download a pinned, hash-verified portable CPU runtime and official Qwen weights."""

import argparse
import hashlib
import json
import sys
import tarfile
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / ".local" / "llm"
WINDOWS = (
    "llama-b11382-bin-win-cpu-x64.zip",
    "https://github.com/ggml-org/llama.cpp/releases/download/b11382/"
    "llama-b11382-bin-win-cpu-x64.zip",
    "40d55282382909be50d27a3e182885860c28ff148e4d952beca7aaad91504051",
)
LINUX = (
    "llama-b11382-bin-ubuntu-x64.tar.gz",
    "https://github.com/ggml-org/llama.cpp/releases/download/b11382/"
    "llama-b11382-bin-ubuntu-x64.tar.gz",
    "34407d59947ed4ab35fe4ab2db5f61bb4d5aedfe25e6a72f702f3ae9758a396d",
)
MODEL = (
    "Qwen3-1.7B-Q8_0.gguf",
    "https://huggingface.co/Qwen/Qwen3-1.7B-GGUF/resolve/"
    "90862c4b9d2787eaed51d12237eafdfe7c5f6077/Qwen3-1.7B-Q8_0.gguf",
    "061b54daade076b5d3362dac252678d17da8c68f07560be70818cace6590cb1a",
)
JUDGE_MODEL = (
    "Qwen3-0.6B-Q8_0.gguf",
    "https://huggingface.co/Qwen/Qwen3-0.6B-GGUF/resolve/"
    "23749fefcc72300e3a2ad315e1317431b06b590a/Qwen3-0.6B-Q8_0.gguf",
    "9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031",
)


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--judge", action="store_true")
    options = parser.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    manifest = []
    if sys.platform not in {"win32", "linux"}:
        raise ValueError("Portable setup supports Windows/Linux x64")
    for name, url, expected in (
        WINDOWS if sys.platform == "win32" else LINUX,
        JUDGE_MODEL if options.judge else MODEL,
    ):
        target = ROOT / name
        if not target.exists() or sha256(target) != expected:
            pending = target.with_suffix(target.suffix + ".partial")
            request = urllib.request.Request(url, headers={"User-Agent": "KarKontrol-setup/1.1"})
            with urllib.request.urlopen(request, timeout=60) as source, pending.open("wb") as out:
                size = 0
                checkpoint = 0
                while block := source.read(1024 * 1024):
                    out.write(block)
                    size += len(block)
                    if size - checkpoint >= 256 * 1024 * 1024:
                        print(f"{name}: {size // (1024 * 1024)} MiB", flush=True)
                        checkpoint = size
            if sha256(pending) != expected:
                raise ValueError(f"Checksum mismatch: {name}")
            pending.replace(target)
        print(f"SHA256 verified: {name}", flush=True)
        manifest.append(
            {"file": name, "url": url, "sha256": expected, "bytes": target.stat().st_size}
        )
        if target.suffix == ".zip":
            destination = ROOT / "runtime"
            destination.mkdir(exist_ok=True)
            with zipfile.ZipFile(target) as archive:
                for entry in archive.infolist():
                    if (
                        not (destination / entry.filename)
                        .resolve()
                        .is_relative_to(destination.resolve())
                    ):
                        raise ValueError("Unsafe archive member")
                archive.extractall(destination)
        elif target.name.endswith(".tar.gz"):
            destination = ROOT / "runtime"
            destination.mkdir(exist_ok=True)
            with tarfile.open(target) as archive:
                archive.extractall(destination, filter="data")
    (ROOT / ("judge-manifest.json" if options.judge else "manifest.json")).write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print("Portable runtime ready; start it on 127.0.0.1 only.")


if __name__ == "__main__":
    main()
