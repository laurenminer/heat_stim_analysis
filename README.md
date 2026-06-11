# heat_stim_analysis

Tools for visualizing heat-stimulation experiments in whole-brain imaging — building the
stimulation signal timeline and rendering annotated, sped-up videos of recordings.

## Scripts
- **`plot_heat_stims.py`** — builds the heat-stim time/value signal (`build_signal`,
  configurable stim minutes over a total duration) and plots it. Figures are written to
  `outputs/plots/`.
- **`make_stim_video.py`** — renders a sped-up `.mp4` from an imaging `.h5`, burning a
  "Heat Stimulation On" overlay onto frames while the stimulus is active (pipes RGB frames to
  `ffmpeg`). Videos are written to `outputs/videos/`. (Requires `ffmpeg` on PATH.)
- **`main.py`** — package entry-point stub.
- **`PrettyHeatStim.ipynb`** — notebook for "pretty" heat-stim visualizations from imaging
  `.h5` data (h5py / OpenCV / matplotlib).

## Requirements
See `pyproject.toml` (numpy, matplotlib, h5py, etc.). `make_stim_video.py` also needs `ffmpeg`.

## Note
`outputs/` (generated plots and videos) is gitignored.
