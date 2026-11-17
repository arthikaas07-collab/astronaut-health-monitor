import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Astronaut Health Monitor",
                   page_icon="🚀", layout="wide")

# key: (label, unit, baseline, noise, limits)
# limits = (warn_low, crit_low, warn_high, crit_high)
METRICS = {
    "heart_rate": ("Heart rate", "bpm", 72, 7,
                   (45, 40, 100, 125)),
    "spo2": ("Blood oxygen", "%", 97, 0.9,
             (94, 90, None, None)),
    "co2_ppm": ("Carbon dioxide", "ppm", 3000, 420,
                (None, None, 4500, 6000)),
    "pressure_kpa": ("Cabin pressure", "kPa", 101, 1.2,
                     (97, 90, None, None)),
    "radiation_usv_h": ("Radiation", "uSv/h", 30, 9,
                        (None, None, 60, 120)),
    "temp_c": ("Body temperature", "C", 36.8, 0.25,
               (36.0, 35.5, 37.6, 38.3)),
}
CREW = ["Asha Rao", "Daniel Okafor", "Lukas Berg", "Mei Tanaka"]
EVENTS = {
    "Asha Rao": {"pressure_kpa": (96, 100, -8)},
    "Daniel Okafor": {"co2_ppm": (60, 70, 3300)},
    "Lukas Berg": {"heart_rate": (130, 140, 38),
                   "temp_c": (110, 150, 1.3)},
    "Mei Tanaka": {"radiation_usv_h": (100, 104, 150)},
}
ICON = {0: "🟢 Normal", 1: "🟠 Warning", 2: "🔴 Critical"}


def status(v, th):
    wl, cl, wh, ch = th
    if (cl is not None and v < cl) or (ch is not None and v > ch):
        return 2
    if (wl is not None and v < wl) or (wh is not None and v > wh):
        return 1
    return 0


@st.cache_data
def make_demo():
    rng = np.random.default_rng(42)
    t = pd.date_range("2026-01-15", periods=168, freq="h")
    frames = []
    for c in CREW:
        df = pd.DataFrame({"time": t, "crew": c})
        for k, m in METRICS.items():
            base, sd = m[2], m[3]
            wave = np.sin(np.arange(168) / 24 * 2 * np.pi) * sd * 0.3
            v = base + rng.normal(0, sd, 168) + wave
            ev = EVENTS.get(c, {}).get(k)
            if ev:
                v[ev[0]:ev[1] + 1] += ev[2]
            df[k] = v.round(2)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def find_alerts(d):
    cols = ["Level", "Vital", "From", "To", "Peak"]
    out = []
    for k, m in METRICS.items():
        if k not in d:
            continue
        label, unit, base, _, th = m
        vals = d[k].to_numpy()
        s = np.array([status(v, th) for v in vals])
        i = 0
        while i < len(d):
            if s[i] == 0:
                i += 1
                continue
            j = i
            while j < len(d) and s[j] > 0:
                j += 1
            seg = vals[i:j]
            peak = seg[np.abs(seg - base).argmax()]
            level = "CRITICAL" if s[i:j].max() == 2 else "warning"
            out.append({
                "Level": level,
                "Vital": label,
                "From": d["time"].iloc[i],
                "To": d["time"].iloc[j - 1],
                "Peak": f"{peak} {unit}",
            })
            i = j
    if not out:
        return pd.DataFrame(columns=cols)
    return pd.DataFrame(out, columns=cols).sort_values("From")


st.title("🚀 Astronaut Health Monitor")
st.caption("NASA Space Apps Challenge. Demo data, placeholder limits.")

up = st.sidebar.file_uploader("Upload your own CSV (optional)",
                              type="csv")
if up:
    data = pd.read_csv(up, parse_dates=["time"])
    st.sidebar.success("Using your CSV")
else:
    data = make_demo()
    st.sidebar.info("Using synthetic demo data")

crew = st.sidebar.selectbox("Crew member", sorted(data["crew"].unique()))
d = data[data["crew"] == crew].sort_values("time").reset_index(drop=True)

st.subheader(f"Latest readings: {crew}")
cols = st.columns(3)
shown = [(k, m) for k, m in METRICS.items() if k in d]
for n, (k, m) in enumerate(shown):
    label, unit, _, _, th = m
    v = d[k].iloc[-1]
    cols[n % 3].metric(label, f"{v} {unit}", ICON[status(v, th)],
                       delta_color="off")

st.subheader("History")
choices = [k for k in METRICS if k in d]
k = st.selectbox("Vital", choices,
                 format_func=lambda x: METRICS[x][0])
label, unit, _, _, th = METRICS[k]

fig, ax = plt.subplots(figsize=(10, 3.6))
ax.plot(d["time"], d[k], color="#2f5cf0", lw=1.6)
colors = ["#c98300", "#d6342f", "#c98300", "#d6342f"]
names = ["warn low", "critical low", "warn high", "critical high"]
for val, col, name in zip(th, colors, names):
    if val is not None:
        ax.axhline(val, color=col, ls="--", lw=1, label=name)
ax.set_ylabel(f"{label} ({unit})")
ax.legend(loc="upper left", fontsize=8)
fig.autofmt_xdate()
st.pyplot(fig)

alerts = find_alerts(d)
st.subheader(f"{len(alerts)} alert events")
st.dataframe(alerts, hide_index=True)
st.download_button("Download alerts as CSV",
                   alerts.to_csv(index=False),
                   "alerts.csv", "text/csv")