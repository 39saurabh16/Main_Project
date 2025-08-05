 #!/usr/bin/env python3
"""
metrics_collector.py
────────────────────
Periodically polls each sensor/host inside a running Mininet‑WiFi
simulation and appends four metrics to metrics_log.csv:

 • latency_ms        – average ICMP RTT to the application server
 • throughput_kbps   – UDP iperf bandwidth host ➜ server
 • pdr               – packet‑delivery‑ratio during a 10‑ping burst
 • energy_mJ         – Contiki/energest total consumption (mocked here)

Requires:
  * Mininet CLI running in a separate terminal (`mininet-wifi>`)
  * iperf3 installed in the Mininet VM and on the “srv” host
  * Each Contiki mote periodically writes its energy to /tmp/<host>_energy.txt
    (replace `_get_energy()` with your real hook)

Usage:
  python3 metrics_collector.py --interval 30
"""

import csv, subprocess, time, datetime, argparse, re, os, sys, shlex

NODES   = ["hr", "tmp", "ecg", "oxy", "bp"]   # add/remove as needed
SERVER  = "srv"

PING_CNT      = 10      # for latency and PDR burst
IPERF_TIME    = 3       # seconds
ENERGY_PATH   = "/tmp"  # folder where sensor logs energy values
CSV_FILE      = "metrics_log.csv"

ping_re   = re.compile(r"min/avg/max.* = .*?/([0-9.]+)/")
pktloss_re= re.compile(r"(\d+)% packet loss")
bw_re     = re.compile(r"([\d.]+)\s+Kbits/sec")

def _mn(cmd: str) -> str:
    """Run a Mininet CLI command via mnexec"""  # mnexec substitutes in namespaces
    return subprocess.check_output(["mnexec", "-a", "1", "sh", "-c", cmd],
                                   text=True, stderr=subprocess.STDOUT)

def _latency_pdr(host: str) -> tuple[float, float]:
    out = _mn(f"{host} ping -c {PING_CNT} {SERVER}")
    avg = float(ping_re.search(out).group(1))
    loss_pct = float(pktloss_re.search(out).group(1))
    pdr = 1.0 - loss_pct/100.0
    return avg, pdr

def _throughput(host: str) -> float:
    # one‑shot UDP iperf3 client; server should be running on srv
    cmd = f"{host} iperf3 -u -b 1M -t {IPERF_TIME} -c {SERVER}"
    out = _mn(cmd)
    m = bw_re.search(out)
    if not m:
        return 0.0
    return float(m.group(1))

def _get_energy(host: str) -> float:
    f = os.path.join(ENERGY_PATH, f"{host}_energy.txt")
    try:
        with open(f) as fp:
            return float(fp.read().strip())
    except FileNotFoundError:
        return 0.0

def main(interval: int):
    first = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", newline="") as fp:
        writer = csv.DictWriter(fp,
            fieldnames=["timestamp", "node",
                        "latency_ms", "throughput_kbps", "pdr", "energy_mJ"])
        if first:
            writer.writeheader()

        while True:
            for h in NODES:
                ts   = datetime.datetime.now().isoformat(timespec="seconds")
                lat, pdr = _latency_pdr(h)
                thr  = _throughput(h)
                eng  = _get_energy(h)

                writer.writerow({
                    "timestamp": ts,
                    "node": h,
                    "latency_ms": round(lat, 2),
                    "throughput_kbps": round(thr, 1),
                    "pdr": round(pdr, 3),
                    "energy_mJ": eng
                })
                print(f"[{ts}] {h:>3}  latency={lat:.1f} ms  thr={thr:.0f} kbps  "
                      f"pdr={pdr:.2f}  energy={eng:.0f} mJ")
                fp.flush()
            time.sleep(interval)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=int, default=60,
                    help="seconds between samples (default 60)")
    args = ap.parse_args()
    try:
        main(args.interval)
    except KeyboardInterrupt:
        sys.exit(0)
