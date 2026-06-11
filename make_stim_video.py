"""
Create a sped-up .mp4 of 2026-03-26-01 with 'Heat Stimulation On' overlay
when heat stim is active. Pipes RGB frames (with text burned in) to ffmpeg.
"""

import subprocess
import signal
import hdf5plugin  # noqa: F401 — registers Blosc decompressor for h5py
import h5py
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

H5_PATH = Path("/store1/lauren/Whole_Brain_Imaging/prj_1560/NGM_NoFood_Heat/data_raw/2026-03-26/2026-03-26-01.h5")
OUTPUT_DIR = Path(__file__).parent / "outputs" / "videos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PATH = OUTPUT_DIR / "2026-03-26-01_heat_stim.mp4"

TARGET_DURATION_S = 240  # ~4 minutes

with h5py.File(H5_PATH, "r") as h:
    n_frames = h["img_nir"].shape[0]
    height, width = h["img_nir"].shape[1], h["img_nir"].shape[2]

    # Build per-frame stim ON/OFF from laser_record
    lr = h["laser_record"][1, 0, :]  # power values (0.0 or 0.1)
    n_lr = lr.shape[0]

    # Timestamps in nanoseconds
    timestamps = h["img_metadata/img_timestamp"][:]
    # img_nir has half as many frames as img_metadata (two channels interleaved)
    ts_nir = timestamps[::2][:n_frames]
    t_sec = (ts_nir - ts_nir[0]) / 1e9  # seconds from start
    total_duration = t_sec[-1]

    # Map each frame to laser_record index
    lr_times = np.linspace(0, total_duration, n_lr)
    stim_on = np.interp(t_sec, lr_times, lr) > 0.05  # True when stim is on

    # Output fps to hit target duration
    output_fps = n_frames / TARGET_DURATION_S
    print(f"Frames: {n_frames}, Size: {width}x{height}")
    print(f"Recording duration: {total_duration:.1f}s, Output fps: {output_fps:.1f}")
    print(f"Target video duration: {n_frames / output_fps:.1f}s")

    # Try to load a nice font, fall back to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
    except OSError:
        font = ImageFont.load_default()
        font_small = font

    # Start ffmpeg — simple pipeline, no filters
    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{width}x{height}",
        "-pix_fmt", "rgb24",
        "-r", f"{output_fps:.2f}",
        "-i", "-",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        str(OUTPUT_PATH),
    ]

    proc = subprocess.Popen(
        cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
        preexec_fn=lambda: signal.signal(signal.SIGPIPE, signal.SIG_DFL),
    )

    # Stream frames with text overlay burned in via Pillow
    chunk_size = 200
    for i in range(0, n_frames, chunk_size):
        end = min(i + chunk_size, n_frames)
        frames = h["img_nir"][i:end]  # (N, H, W) uint8

        for j in range(frames.shape[0]):
            fidx = i + j
            # Convert grayscale to RGB
            frame_rgb = np.stack([frames[j]] * 3, axis=-1)
            img = Image.fromarray(frame_rgb)
            draw = ImageDraw.Draw(img)

            # Overlay stim text
            if stim_on[fidx]:
                draw.text((15, 12), "Heat Stimulation On", fill=(255, 50, 50), font=font)

            # Overlay real elapsed time
            elapsed = t_sec[fidx]
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            draw.text((15, height - 35), f"t = {mins:02d}:{secs:02d}", fill=(255, 255, 255), font=font_small)

            try:
                proc.stdin.write(np.array(img).tobytes())
            except BrokenPipeError:
                break

        if (i // chunk_size) % 10 == 0:
            pct = 100 * end / n_frames
            print(f"  {pct:5.1f}%  frames {i}-{end} / {n_frames}", flush=True)

    try:
        proc.stdin.close()
    except BrokenPipeError:
        pass
    proc.stdin = None  # prevent communicate() from flushing closed stdin
    _, stderr = proc.communicate()

    if proc.returncode != 0:
        print("ffmpeg error:")
        print(stderr.decode()[-2000:])
    else:
        print(f"\nSaved: {OUTPUT_PATH}")
        print(f"Video duration: ~{n_frames / output_fps:.0f}s ({n_frames / output_fps / 60:.1f} min)")
