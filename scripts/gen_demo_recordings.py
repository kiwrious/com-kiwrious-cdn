#!/usr/bin/env python3
"""Generate back-dated demo recordings for measure.kiwrious.com.

Each recording is written as its own `.kiwrious` backup file (the same JSON
format the Measure app's Export/Import uses), plus an `index.json` manifest
the app reads for its "Demos" button.

    python3 scripts/gen_demo_recordings.py

Output: measure/demo-recordings/*.kiwrious + index.json
Deterministic (fixed seeds) so re-running produces identical files.
"""

import json
import math
import random
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

OUT = Path(__file__).resolve().parent.parent / "measure" / "demo-recordings"
TZ = ZoneInfo("Pacific/Auckland")
KIND = "kiwrious-recordings-backup"


def ms(y, mo, d, h, mi, s=0):
    return int(datetime(y, mo, d, h, mi, s, tzinfo=TZ).timestamp() * 1000)


def smooth_noise(rng, n, scale, alpha=0.15):
    """Low-pass filtered noise — looks like slow sensor drift, not static."""
    v, out = 0.0, []
    for _ in range(n):
        v += alpha * (rng.gauss(0, scale) - v)
        out.append(v)
    return out


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def logistic(t, t0, k):
    return 1 / (1 + math.exp(-(t - t0) / k))


# ---------------------------------------------------------------- recordings
# Each builder returns (series_dict, n) where series_dict maps label -> [y]


def walk_to_school(rng, n, dt):
    # Outdoor walk, partly cloudy: shade from trees + passing clouds.
    lux, uv = [], []
    cloud = smooth_noise(rng, n, 1.0, 0.05)
    for i in range(n):
        t = i * dt
        base = 62000 + 9000 * math.sin(t / 900)          # sun climbing
        shade = 0.35 if 300 < t < 420 or 780 < t < 840 else 1.0  # tree-lined streets
        c = clamp(1 - 0.45 * max(0, cloud[i]), 0.35, 1.0)
        l = base * shade * c * (1 + rng.gauss(0, 0.03))
        lux.append(round(l))
        uv.append(round(clamp(l / 9000 + rng.gauss(0, 0.15), 0, 12), 1))
    return {"Lux": lux, "Uv": uv}


def sunscreen_test(rng, n, dt):
    # Bare sensor in midday sun, then covered by cling film, then film + SPF50.
    lux, uv = [], []
    for i in range(n):
        t = i * dt
        if t < 40:
            u, l = 8.6, 88000
        elif t < 50:
            u, l = None, 9000      # hand over sensor while wrapping film
        elif t < 90:
            u, l = 7.9, 82000      # cling film: barely blocks UV
        elif t < 100:
            u, l = None, 12000     # applying sunscreen
        else:
            u, l = 0.6, 61000      # SPF50 smear: UV blocked, light mostly passes
        if u is None:
            u = rng.uniform(0.2, 1.2)
        uv.append(round(clamp(u + rng.gauss(0, 0.12), 0, 12), 1))
        lux.append(round(l * (1 + rng.gauss(0, 0.02))))
    return {"Lux": lux, "Uv": uv}


def classroom_lights(rng, n, dt):
    # Lights on -> off -> blinds open -> lights on again (indoors, UV ~0).
    lux, uv = [], []
    for i in range(n):
        t = i * dt
        if t < 30:
            l = 480
        elif t < 60:
            l = 55
        elif t < 95:
            l = 55 + 1400 * logistic(t, 70, 3)   # blinds opened
        else:
            l = 1880
        lux.append(round(l * (1 + rng.gauss(0, 0.015))))
        uv.append(round(clamp((0.3 if t >= 70 else 0.0) + rng.gauss(0, 0.04), 0, 12), 1))
    return {"Lux": lux, "Uv": uv}


def bathroom_shower(rng, n, dt):
    # Shower runs 10 min then extractor fan clears the steam.
    hum, temp = [], []
    dh = smooth_noise(rng, n, 0.8, 0.2)
    for i in range(n):
        t = i * dt
        if t < 120:
            h, c = 58, 18.6
        elif t < 720:
            p = 1 - math.exp(-(t - 120) / 180)
            h, c = 58 + 36 * p, 18.6 + 4.6 * p
        else:
            p = math.exp(-(t - 720) / 900)
            h, c = 60 + 34 * p, 19.4 + 3.8 * p
        hum.append(round(clamp(h + dh[i], 0, 99), 1))
        temp.append(round(c + rng.gauss(0, 0.05), 1))
    return {"Temp": temp, "Hum": hum}


def breath_test(rng, n, dt):
    # Three slow breaths onto the sensor.
    hum, temp = [], []
    for i in range(n):
        t = i * dt
        h, c = 46, 21.2
        for b in (10, 28, 46):
            if t >= b:
                k = math.exp(-(t - b) / 4)
                h += 38 * k * min(1, (t - b) / 1.5)
                c += 3.2 * k * min(1, (t - b) / 1.5)
        hum.append(round(h + rng.gauss(0, 0.3), 1))
        temp.append(round(c + rng.gauss(0, 0.04), 1))
    return {"Temp": temp, "Hum": hum}


def bedroom_overnight(rng, n, dt):
    # 10 pm -> 6 am. Heater off at 11, window cracked, someone sleeping.
    hum, temp = [], []
    dt_n = smooth_noise(rng, n, 0.25, 0.08)
    for i in range(n):
        hrs = i * dt / 3600
        c = 21.5 - 5.0 * (1 - math.exp(-max(0, hrs - 1) / 2.2))
        if hrs > 7.5:
            c += 1.6 * (hrs - 7.5) / 0.5   # heater back on at 5:30
        h = 52 + 11 * (1 - math.exp(-hrs / 3)) - 0.9 * (c - 16.5)
        temp.append(round(c + dt_n[i], 1))
        hum.append(round(clamp(h + rng.gauss(0, 0.4), 0, 100), 1))
    return {"Temp": temp, "Hum": hum}


def tea_cooling(rng, n, dt):
    # IR pointed at a mug of tea (Newton's law of cooling); ambient stable.
    amb, ir = [], []
    for i in range(n):
        t = i * dt
        surf = 21.4 + (71.0 - 21.4) * math.exp(-t / 1150)
        if 600 <= t < 615:
            surf -= 6   # milk poured in
        ir.append(round(surf + rng.gauss(0, 0.15), 1))
        amb.append(round(21.4 + 0.3 * math.sin(t / 400) + rng.gauss(0, 0.05), 1))
    return {"AmbientTemp": amb, "InfraredTemp": ir}


def forehead_check(rng, n, dt):
    # Room surface -> forehead -> palm -> forehead again.
    amb, ir = [], []
    for i in range(n):
        t = i * dt
        if t < 6:
            v = 23.8
        elif t < 18:
            v = 36.6 - 12.8 * math.exp(-(t - 6) / 0.8)
        elif t < 26:
            v = 33.4
        elif t < 30:
            v = 24.5
        else:
            v = 36.5 - 12 * math.exp(-(t - 30) / 0.8)
        ir.append(round(v + rng.gauss(0, 0.08), 1))
        amb.append(round(22.6 + rng.gauss(0, 0.03), 1))
    return {"AmbientTemp": amb, "InfraredTemp": ir}


def water_tasting(rng, n, dt):
    # Probe dipped in 4 cups, rinsed/dried (reads ~0) in between.
    segments = [(0, 8, 0.0), (8, 30, 4.2), (30, 38, 0.0), (38, 62, 268),
                (62, 70, 0.0), (70, 94, 835), (94, 102, 0.0), (102, 130, 41800)]
    con = []
    prev = 0.0
    for i in range(n):
        t = i * dt
        target = next((v for a, b, v in segments if a <= t < b), 0.0)
        prev += (target - prev) * 0.55        # probe settling
        noise = 1 + rng.gauss(0, 0.012)
        con.append(round(max(0, prev * noise), 1))
    return {"Con": con}


def dissolving_salt(rng, n, dt):
    # Teaspoons of salt stirred into 250 ml tap water.
    con = []
    for i in range(n):
        t = i * dt
        v = 260
        for s in (20, 70, 120):
            v += 5200 * logistic(t, s + 12, 5)
        con.append(round(v * (1 + rng.gauss(0, 0.008)), 1))
    return {"Con": con}


def cooking_dinner(rng, n, dt):
    # Kitchen VOC while frying onions; range hood on at 25 min.
    voc = []
    drift = smooth_noise(rng, n, 20, 0.1)
    for i in range(n):
        m = i * dt / 60
        v = 85
        if m > 5:
            v += 950 * (1 - math.exp(-(m - 5) / 6))
        if m > 25:
            v = 85 + (v - 85) * math.exp(-(m - 25) / 5)
        voc.append(int(max(0, v + drift[i])))
    return {"Voc": voc}


def sanitiser_sniff(rng, n, dt):
    voc = []
    for i in range(n):
        t = i * dt
        v = 60
        if t >= 15:
            v += 2600 * math.exp(-(t - 15) / 14) * min(1, (t - 15) / 2)
        voc.append(int(v + rng.gauss(0, 6)))
    return {"Voc": voc}


def jumping_jacks(rng, n, dt):
    hr = []
    v = 74.0
    for i in range(n):
        t = i * dt
        if t < 40:
            target = 74
        elif t < 100:
            target = 148
        else:
            target = 80
        tau = 9 if target > v else 22
        v += (target - v) * dt / tau
        hr.append(int(round(v + rng.gauss(0, 1.2))))
    return {"HeartRate": hr}


def breathing_exercise(rng, n, dt):
    # 4-7-8 breathing: respiratory sinus arrhythmia, slow downward trend.
    hr = []
    for i in range(n):
        t = i * dt
        base = 78 - 10 * (1 - math.exp(-t / 60))
        rsa = 4.5 * math.sin(2 * math.pi * t / 19)
        hr.append(int(round(base + rsa + rng.gauss(0, 0.8))))
    return {"HeartRate": hr}


# (slug, name, sensorType, sampleRateHz, durationS, startedAt, builder)
RECORDINGS = [
    ("walk-to-school", "Walk to school — sun & shade", "UV", 1 / 5, 1200, ms(2026, 10, 27, 8, 12), walk_to_school),
    ("sunscreen-test", "Sunscreen vs cling film", "UV", 1, 130, ms(2026, 11, 3, 12, 41), sunscreen_test),
    ("classroom-lights", "Classroom lights & blinds", "UV", 1, 140, ms(2026, 11, 12, 10, 5), classroom_lights),
    ("bathroom-shower", "Bathroom during a hot shower", "HUMIDITY", 1 / 5, 2400, ms(2026, 10, 30, 7, 2), bathroom_shower),
    ("breath-test", "Three breaths on the sensor", "HUMIDITY", 1, 70, ms(2026, 11, 10, 14, 22), breath_test),
    ("bedroom-overnight", "Bedroom overnight", "HUMIDITY", 1 / 60, 8 * 3600, ms(2026, 11, 5, 22, 0), bedroom_overnight),
    ("tea-cooling", "Cup of tea cooling down", "TEMPERATURE", 1 / 5, 1800, ms(2026, 11, 8, 15, 30), tea_cooling),
    ("forehead-check", "Forehead & palm check", "TEMPERATURE", 1, 45, ms(2026, 11, 17, 9, 48), forehead_check),
    ("water-tasting", "Distilled, tap, mineral & sea water", "CONDUCTIVITY", 1, 130, ms(2026, 11, 4, 11, 15), water_tasting),
    ("dissolving-salt", "Dissolving salt, one spoon at a time", "CONDUCTIVITY", 1, 180, ms(2026, 11, 14, 13, 3), dissolving_salt),
    ("cooking-dinner", "Kitchen air while cooking", "VOC", 1 / 5, 2700, ms(2026, 11, 1, 18, 20), cooking_dinner),
    ("sanitiser-sniff", "Hand sanitiser near the sensor", "VOC", 1, 90, ms(2026, 11, 19, 10, 37), sanitiser_sniff),
    ("jumping-jacks", "Resting vs jumping jacks", "HEART_RATE", 1, 180, ms(2026, 11, 11, 11, 30), jumping_jacks),
    ("breathing-exercise", "4-7-8 breathing exercise", "HEART_RATE", 1, 150, ms(2026, 11, 18, 20, 45), breathing_exercise),
]

SERIES_ORDER = {
    "UV": ["Lux", "Uv"],
    "HUMIDITY": ["Temp", "Hum"],
    "TEMPERATURE": ["AmbientTemp", "InfraredTemp"],
    "CONDUCTIVITY": ["Con"],
    "VOC": ["Voc"],
    "HEART_RATE": ["HeartRate"],
}


def stats(ys):
    return {"min": min(ys), "max": max(ys), "avg": round(sum(ys) / len(ys), 3)}


def build(idx, slug, name, sensor, rate, duration, started, builder):
    rng = random.Random(f"kiwrious-demo-{slug}")
    dt = 1 / rate
    n = int(duration * rate)
    values = builder(rng, n, dt)
    # x matches chart.js: first sample at one time-step, rounded to 3 dp.
    xs = [round((i + 1) * dt, 3) for i in range(n)]
    series = [{"name": lbl, "data": [{"x": x, "y": y} for x, y in zip(xs, values[lbl])]}
              for lbl in SERIES_ORDER[sensor]]
    rec = {
        "id": idx + 1,
        "demoId": f"demo:{slug}",
        "name": name,
        "sensorType": sensor,
        "sampleRate": rate,
        "startedAt": started,
        # Wall-clock start; the app re-bases startedAt on this so demo times
        # read naturally (e.g. 8:12 am) in whatever timezone the viewer is in.
        "startedAtLocal": datetime.fromtimestamp(started / 1000, TZ).strftime("%Y-%m-%dT%H:%M:%S"),
        "durationS": int(duration),
        "series": series,
        "stats": {s["name"]: stats([p["y"] for p in s["data"]]) for s in series},
    }
    return rec


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.kiwrious"):
        old.unlink()
    index = []
    for i, args in enumerate(RECORDINGS):
        rec = build(i, *args)
        fname = f"{datetime.fromtimestamp(rec['startedAt'] / 1000, TZ):%Y-%m-%d}_{args[0]}.kiwrious"
        payload = {
            "kind": KIND,
            "version": 1,
            "exportedAt": datetime.fromtimestamp(rec["startedAt"] / 1000 + rec["durationS"] + 5, TZ).isoformat(),
            "count": 1,
            "recordings": [rec],
        }
        (OUT / fname).write_text(json.dumps(payload, separators=(",", ":"), ensure_ascii=False))
        index.append({
            "file": fname,
            "demoId": rec["demoId"],
            "name": rec["name"],
            "sensorType": rec["sensorType"],
            "startedAt": rec["startedAt"],
            "durationS": rec["durationS"],
            "samples": len(rec["series"][0]["data"]),
        })
        print(f"{fname:48s} {len(rec['series'][0]['data']):5d} samples  {rec['stats']}")
    index.sort(key=lambda e: e["startedAt"], reverse=True)
    (OUT / "index.json").write_text(json.dumps(
        {"kind": "kiwrious-demo-recordings", "version": 1, "recordings": index}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
