# Kiwrious Play demo projects

Ready-made Scratch 3 projects (`.sb3`) for [Kiwrious Play](https://play.kiwrious.com/), the
Scratch fork with the **Kiwrious** blocks for Kiwrious USB sensors. `index.json` lists every demo
with its sensor, how to test it, and a challenge idea.

| File | Sensor | What it does |
|------|--------|--------------|
| `breathing-exercise.sb3` | Humidity | Breathe on the sensor to inflate a balloon |
| `hungry-parrot.sb3` | Light | Steer a parrot with light and catch strawberries |
| `hedgehog-and-light.sb3` | Light + webcam | A hedgehog wakes up when it gets bright |
| `uv-graph-video.sb3` | UV + webcam | Live UV graph over the webcam picture |
| `voc-smell-detector.sb3` | VOC | Sniffy reacts to smells (tVOC meter) |
| `salty-water-tester.sb3` | Conductivity | A bulb lights up when the water conducts |
| `hot-or-cold.sb3` | IR temperature | Thermometer gun: COLD / WARM / HOT |
| `sunscreen-test.sb3` | UV | How much UV does sunscreen block? |
| `live-graph.sb3` | Any | Auto-scaling live line graph of any reading |
| `sensor-band.sb3` | Light (any) | Play music by waving your hand over the sensor |

## Load a demo

1. Download the `.sb3` file, e.g. `https://cdn.kiwrious.com/play/demos/hot-or-cold.sb3`.
2. Open <https://play.kiwrious.com/> in **Chrome or Edge on a computer** (they support Web Serial).
3. Choose **File > Load from your computer** and pick the file.
4. Click the **green flag**.

## Connect the sensor

* **New demos (last six above):** click the orange **Connect sensor** button on the stage, then pick
  the Kiwrious sensor in the browser pop-up. The button turns green ("Sensor connected") once readings
  arrive. If you cancel the pop-up or plug in the wrong sensor, it goes back to orange with a hint.
* **Older demos (first four):** clicking the green flag opens the sensor pop-up straight away.

If you click the red stop sign or the green flag again, the sensor stops reading. Click
**Connect sensor** again to carry on.

## Demo mode (no sensor needed)

Each of the six new demos has a **Demo mode (D)** button in the bottom-right corner:

1. Click the green flag.
2. Press **D** on the keyboard (or click the button). It turns purple and a **demo value** slider
   appears.
3. Drag the slider, or use the **up/down arrow keys**, to make up a sensor reading. The demo reacts
   just as it would to a real sensor.

Press **D** again, or click **Connect sensor**, to leave demo mode. The four older demos don't have
a demo mode and need a real sensor.

## Notes

* The VOC sensor needs about 15 seconds to warm up after you plug it in.
* The UV index is usually close to 0 indoors and behind glass, so do the sunscreen test outside.
* Every project uses plain Scratch blocks. Click **See inside** (or open the Code tab) to change
  thresholds, colours or sounds.
