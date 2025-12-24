# encoding_video-2-mp4

[(Korean)](README.md)

A simple script that re-encodes video files (mp4, mov, ...) in a folder to H.264.
By default, it performs in-place re-encoding that replaces the original. You can
also keep the original and save a new file.

## Apply to other code (request prompt)

Even if you don't use this repo directly, you can ask an AI agent to adjust the
"video save/encode" part in your existing code to match the spec below.

```
You are a software engineer AI agent. Ensure that all MP4s generated/stored in our system
are saved with the "target encoding spec" below.

[Target Encoding Spec]
- Container: MP4
- Video codec: H.264/AVC (libx264), profile=high, pix_fmt=yuv420p
- Frame rate: keep source (no change)
- Bitrate: ~2420 kbps (b:v=2420k, maxrate=2420k, bufsize=4840k)
- B-frames: 2 (bf=2)
- Audio: strip (-an)
- MP4 optimization: faststart (+faststart)
```

## Features

- Batch re-encode video files in a folder
- Recursive traversal of subfolders
- In-place replace or keep original + write new file
- Dry-run to preview targets

## Requirements

- Python 3.9+
- `ffmpeg` (available in PATH)

## Input extensions

Handles the extensions below. Add more in `main.py` under `VIDEO_EXTENSIONS` if needed.

`.mp4`, `.mov`, `.m4v`, `.mkv`, `.avi`, `.webm`, `.mpg`, `.mpeg`, `.ts`,
`.mts`, `.m2ts`, `.wmv`, `.flv`, `.3gp`

## Usage

```bash
python main.py /path/to/folder
```

Options:

- `--recursive`: recursively process subfolders
- `--keep-original`: keep original and create a new file
- `--suffix <str>`: suffix for new filename (default: `_reencoded`)
- `--dry-run`: list targets only (no actual conversion)

## Examples

Replace originals and process recursively:

```bash
python main.py /path/to/folder --recursive
```

Keep originals and create new files:

```bash
python main.py /path/to/folder --keep-original --suffix _reencoded
```

Dry-run to preview targets:

```bash
python main.py /path/to/folder --dry-run
```

You can also refer to `run.sh`. Update the path and options as needed.

## Encoding settings

`main.py` calls `ffmpeg` with the settings below in `transcode_to_temp()`.

- Video codec: H.264 (`libx264`)
- Profile: `high`
- Pixel format: `yuv420p`
- Frame rate: keep source
- Bitrate: 2420k (maxrate 2420k, bufsize 4840k)
- B-frames: 2
- Audio: `-an`
- faststart enabled

## Behavior / Notes

- Creates a temp file (`*.tmp_transcode.mp4`) and replaces the original on success.
- Even if the input is not MP4, the output is saved as MP4, and it fails if a file
  with the same MP4 name already exists.
- On failure, the original remains and the temp file is cleaned up.
- With `--keep-original`, saves as `<stem>_reencoded.mp4` and increments with
  `_reencoded_001` if needed.
