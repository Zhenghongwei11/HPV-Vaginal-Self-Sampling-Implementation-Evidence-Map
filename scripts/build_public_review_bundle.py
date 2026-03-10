#!/usr/bin/env python3
import argparse
import hashlib
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


FIXED_ZIP_DT = (2026, 3, 10, 0, 0, 0)


def iter_files(repo_root: Path) -> list[Path]:
    out: list[Path] = []
    for path in repo_root.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(repo_root)
        if rel.parts[0] == ".git":
            continue
        if rel.parts[0] in {"dist", "tmp", ".venv", "venv"}:
            continue
        out.append(path)
    return sorted(out, key=lambda p: p.relative_to(repo_root).as_posix())


def write_zip(repo_root: Path, out_zip: Path) -> None:
    out_zip.parent.mkdir(parents=True, exist_ok=True)
    files = iter_files(repo_root)
    with ZipFile(out_zip, "w", compression=ZIP_DEFLATED) as zf:
        for path in files:
            rel = path.relative_to(repo_root).as_posix()
            info = ZipInfo(rel)
            info.date_time = FIXED_ZIP_DT
            info.compress_type = ZIP_DEFLATED
            # Normalize permissions (rw-r--r--) to avoid platform variance.
            info.external_attr = (0o644 & 0xFFFF) << 16
            with path.open("rb") as f:
                zf.writestr(info, f.read())


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a deterministic public review bundle ZIP + checksums.")
    parser.add_argument("--repo-root", default=".", help="Repo root to package.")
    parser.add_argument("--out-dir", default="dist", help="Output directory.")
    parser.add_argument("--version", default="v1.0.1", help="Version tag to embed in filename.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    zip_name = f"public_review_bundle_{args.version}.zip"
    out_zip = out_dir / zip_name
    write_zip(repo_root, out_zip)

    sums_path = out_dir / "CHECKSUMS.sha256"
    digest = sha256(out_zip)
    sums_path.write_text(f"{digest}  {zip_name}{os.linesep}", encoding="utf-8")

    print(f"[bundle] Wrote {out_zip}")
    print(f"[bundle] Wrote {sums_path}")


if __name__ == "__main__":
    main()
