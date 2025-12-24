import argparse
import os
import subprocess
from pathlib import Path
from typing import Iterable


def iter_mp4_files(folder: Path, recursive: bool) -> list[Path]:
    pattern = "**/*.mp4" if recursive else "*.mp4"
    files = list(folder.glob(pattern))
    files += list(folder.glob(("**/*.MP4" if recursive else "*.MP4")))
    return sorted({f.resolve() for f in files if f.is_file()})


def transcode_to_temp(input_mp4: Path) -> Path:
    """
    input_mp4와 같은 폴더에 임시 파일 생성 후 (1)과 유사 세팅으로 H.264 재인코딩.
    """
    tmp_out = input_mp4.with_suffix(input_mp4.suffix + ".tmp_transcode.mp4")
    if tmp_out.exists():
        tmp_out.unlink()

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(input_mp4),

        "-c:v", "libx264",
        "-profile:v", "high",
        "-pix_fmt", "yuv420p",
        "-r", "2",

        "-b:v", "2420k",
        "-maxrate", "2420k",
        "-bufsize", "4840k",

        "-bf", "2",

        "-an",
        "-movflags", "+faststart",

        str(tmp_out),
    ]
    subprocess.run(cmd, check=True)
    return tmp_out


def safe_cleanup(path: Path) -> None:
    try:
        if path.exists():
            path.unlink()
    except Exception:
        pass


def replace_in_place(original: Path, tmp_out: Path) -> None:
    os.replace(str(tmp_out), str(original))


def keep_original_and_write_new(original: Path, tmp_out: Path, suffix: str = "_reencoded") -> Path:
    """
    원본을 남기고 같은 폴더에 새 파일로 저장.
    기본 파일명: <stem>_reencoded.mp4 (동명 충돌 시 _reencoded_001 ...)
    """
    parent = original.parent
    base = f"{original.stem}{suffix}.mp4"
    out = parent / base

    idx = 1
    while out.exists():
        out = parent / f"{original.stem}{suffix}_{idx:03d}.mp4"
        idx += 1

    os.replace(str(tmp_out), str(out))  # tmp_out -> out (원자적 이동)
    return out


def reencode_folder(
    folder: Path,
    recursive: bool = False,
    in_place: bool = True,
    suffix: str = "_reencoded",
    dry_run: bool = False,
) -> None:
    if not folder.exists() or not folder.is_dir():
        raise ValueError(f"유효한 폴더가 아닙니다: {folder}")

    mp4_files = iter_mp4_files(folder, recursive)
    if not mp4_files:
        print("처리할 mp4 파일이 없습니다.")
        return

    print(f"대상 폴더: {folder}")
    print(f"재귀 탐색: {recursive}")
    print(f"모드: {'원본 교체(in-place)' if in_place else '원본 유지 + 새 파일 생성'}")
    if not in_place:
        print(f"새 파일 suffix: {suffix}")
    print(f"대상 파일 수: {len(mp4_files)}")
    if dry_run:
        print("DRY RUN: 실제 인코딩/쓰기 작업은 수행하지 않습니다.\n")

    success, failed = 0, 0

    for i, f in enumerate(mp4_files, 1):
        print(f"[{i}/{len(mp4_files)}] 처리: {f}")
        tmp_candidate = f.with_suffix(f.suffix + ".tmp_transcode.mp4")
        try:
            if dry_run:
                print("  - (dry-run) ffmpeg 인코딩 후", "원본 교체 예정" if in_place else "새 파일 생성 예정")
                success += 1
                continue

            tmp_out = transcode_to_temp(f)

            if not tmp_out.exists() or tmp_out.stat().st_size == 0:
                raise RuntimeError("임시 출력 파일이 생성되지 않았거나 크기가 0입니다.")

            if in_place:
                replace_in_place(f, tmp_out)
                print("  - 완료: 원본을 재인코딩 결과로 교체했습니다.")
            else:
                new_path = keep_original_and_write_new(f, tmp_out, suffix=suffix)
                print(f"  - 완료: 원본 유지, 새 파일 생성 -> {new_path}")

            success += 1

        except Exception as e:
            failed += 1
            print(f"  - 실패: {e}")
            # 실패 시 임시파일 정리 (원본은 건드리지 않음)
            safe_cleanup(tmp_candidate)

    print("\n요약")
    print(f"  성공: {success}")
    print(f"  실패: {failed}")
    if failed:
        print("  실패한 파일은 원본이 그대로 남아 있습니다.")


def main():
    parser = argparse.ArgumentParser(
        description="폴더 내 MP4를 (1)과 유사 세팅으로 H.264 재인코딩합니다. 기본은 원본 교체입니다."
    )
    parser.add_argument("folder", type=str, help="대상 폴더 경로")
    parser.add_argument("--recursive", action="store_true", help="하위 폴더까지 재귀적으로 처리")
    parser.add_argument(
        "--keep-original",
        action="store_true",
        help="원본을 유지하고 새 파일을 생성합니다. (기본: 원본 교체)",
    )
    parser.add_argument(
        "--suffix",
        type=str,
        default="_reencoded",
        help="--keep-original 사용 시 새 파일명에 붙일 suffix (기본: _reencoded)",
    )
    parser.add_argument("--dry-run", action="store_true", help="대상만 확인(실제 변환/쓰기 없음)")

    args = parser.parse_args()

    reencode_folder(
        folder=Path(args.folder),
        recursive=args.recursive,
        in_place=(not args.keep_original),  # 디폴트: 교체
        suffix=args.suffix,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
