 #!/usr/bin/env python3
"""
plot_metrics.py
────────────────
Reads metrics_log.csv and creates four separate PNG files:

 • latency_ms.png
 • throughput_kbps.png
 • pdr.png
 • energy_mJ.png
"""
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

CSV_FILE = "metrics_log.csv"
df = pd.read_csv(CSV_FILE, parse_dates=["timestamp"])

metrics = ["latency_ms", "throughput_kbps", "pdr", "energy_mJ"]

for metric in metrics:
    plt.figure()
    for node, g in df.groupby("node"):
        plt.plot(g["timestamp"], g[metric], label=node, linewidth=1)
    plt.xlabel("Time")
    plt.ylabel(metric.replace("_", " ").title())
    plt.title(f"{metric.replace('_', ' ').title()} per node")
    plt.legend()
    plt.tight_layout()
    png_path = Path(f"{metric}.png")
    plt.savefig(png_path)
    plt.close()
    print(f"Saved {png_path}")

print("✅  All graphs generated.")
