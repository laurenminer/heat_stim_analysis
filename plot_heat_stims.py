import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent / "outputs" / "plots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def build_signal(stim_minutes, total_seconds=960):
    """Build a time/value signal for given stimulation minutes."""
    times = [0]
    values = [0]  # start OFF

    for m in stim_minutes:
        t0 = m * 60  # start of stimulation minute
        # ON for 10s
        times.extend([t0, t0])
        values.extend([0, 1])
        times.extend([t0 + 10, t0 + 10])
        values.extend([1, 0])
        # OFF for 10s (already 0)
        # ON for 10s
        times.extend([t0 + 20, t0 + 20])
        values.extend([0, 1])
        times.extend([t0 + 30, t0 + 30])
        values.extend([1, 0])

    times.append(total_seconds)
    values.append(0)
    return np.array(times) / 60.0, np.array(values)  # convert to minutes


fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 6), sharex=True)

# --- Top plot: Every Minute (minutes 1–14) ---
stim_minutes_top = list(range(1, 15))  # 1 through 14
t1, v1 = build_signal(stim_minutes_top)
ax1.plot(t1, v1, color='red', linewidth=1.5)
ax1.set_title("Heat Stimulation Every Minute", fontsize=14, fontweight='bold')
ax1.set_ylabel("Heat Stimulation", fontsize=12)
ax1.set_yticks([0, 1])
ax1.set_yticklabels(["OFF", "ON"])
ax1.set_xlim(0, 16)
ax1.set_xticks(range(0, 17))
ax1.set_ylim(-0.1, 1.3)
ax1.grid(axis='x', linestyle='--', alpha=0.3)

# --- Bottom plot: Every Other Minute (minutes 1,3,5,7,9,11,13) ---
stim_minutes_bot = list(range(1, 14, 2))  # 1,3,5,7,9,11,13
t2, v2 = build_signal(stim_minutes_bot)
ax2.plot(t2, v2, color='red', linewidth=1.5)
ax2.set_title("Heat Stimulation Every Other Minute", fontsize=14, fontweight='bold')
ax2.set_ylabel("Heat Stimulation", fontsize=12)
ax2.set_xlabel("Time (minutes)", fontsize=12)
ax2.set_yticks([0, 1])
ax2.set_yticklabels(["OFF", "ON"])
ax2.set_xlim(0, 16)
ax2.set_xticks(range(0, 17))
ax2.set_ylim(-0.1, 1.3)
ax2.grid(axis='x', linestyle='--', alpha=0.3)

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "heat_stimulation_protocols.png", dpi=200, bbox_inches='tight')
plt.close()
print(f"Saved to {OUTPUT_DIR / 'heat_stimulation_protocols.png'}")
