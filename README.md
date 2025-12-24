# encoding_mp4-2-mp4

폴더 내 MP4 파일을 H.264로 재인코딩하는 간단한 스크립트입니다. 기본 동작은
원본을 대체하는 in-place 재인코딩이며, 필요 시 원본을 유지하고 새 파일로
저장할 수도 있습니다.

## 다른 코드에 적용하기 (요청 문구)

이 레포를 직접 사용하지 않더라도, 기존 코드에서 “영상 저장/인코딩” 부분을
아래 스펙으로 맞추도록 AI agent에게 요청하면 동일한 결과로 저장할 수 있습니다.

```
당신은 소프트웨어 엔지니어 AI agent입니다. 우리 시스템에서 생성/저장되는 모든 MP4가
아래 “타깃 인코딩 스펙”으로 저장되도록 코드를 적용하세요.

[타깃 인코딩 스펙]
- 컨테이너: MP4
- 비디오 코덱: H.264/AVC (libx264), profile=high, pix_fmt=yuv420p
- 프레임레이트: 원본 유지 (변경 없음)
- 비트레이트: 약 2420 kbps (b:v=2420k, maxrate=2420k, bufsize=4840k)
- B-frames: 2 (bf=2)
- 오디오: 제거(-an)
- MP4 최적화: faststart (+faststart)
```

## 주요 기능

- 지정 폴더의 영상 파일을 일괄 재인코딩
- 하위 폴더 재귀 처리 지원
- 원본 교체 또는 원본 유지 + 새 파일 생성 모드
- dry-run으로 대상만 미리 확인

## 요구사항

- Python 3.9+
- `ffmpeg` (PATH에 등록되어 있어야 함)

## 입력 확장자

아래 확장자를 입력으로 처리합니다. 필요 시 `main.py`의 `VIDEO_EXTENSIONS`에 추가하세요.

`.mp4`, `.mov`, `.m4v`, `.mkv`, `.avi`, `.webm`, `.mpg`, `.mpeg`, `.ts`,
`.mts`, `.m2ts`, `.wmv`, `.flv`, `.3gp`

## 사용법

```bash
python main.py /path/to/folder
```

옵션:

- `--recursive`: 하위 폴더까지 재귀적으로 처리
- `--keep-original`: 원본을 유지하고 새 파일 생성
- `--suffix <str>`: 새 파일명 suffix (기본: `_reencoded`)
- `--dry-run`: 변환하지 않고 대상만 출력

## 예시

원본을 교체하며 재귀적으로 처리:

```bash
python main.py /path/to/folder --recursive
```

원본을 유지하고 새 파일 생성:

```bash
python main.py /path/to/folder --keep-original --suffix _reencoded
```

dry-run으로 대상만 확인:

```bash
python main.py /path/to/folder --dry-run
```

`run.sh`를 참고해도 됩니다. 경로와 옵션을 원하는 대로 수정해 사용하세요.

## 인코딩 설정

`main.py`의 `transcode_to_temp()`에서 아래 설정으로 `ffmpeg`를 호출합니다.

- 비디오 코덱: H.264 (`libx264`)
- 프로파일: `high`
- 픽셀 포맷: `yuv420p`
- 프레임레이트: 원본 유지
- 비트레이트: 2420k (maxrate 2420k, bufsize 4840k)
- B-frames: 2
- 오디오 제거: `-an`
- faststart 적용



## 동작 방식/주의사항

- 임시 파일(`*.tmp_transcode.mp4`)을 만든 뒤 성공 시 원본을 교체합니다.
- 입력이 MP4가 아니더라도 결과는 MP4로 저장되며, 동일한 이름의 MP4가 이미 있으면 실패합니다.
- 실패 시 원본은 유지되며, 임시 파일은 정리됩니다.
- `--keep-original` 모드에서는 `<stem>_reencoded.mp4`로 저장하며,
  동일 파일명이 있으면 `_reencoded_001`처럼 증가합니다.
