"""Run the thermostat model and save a plot as thermostat.png.

Drafted by Claude as a starting point. Not yet reviewed by a person.

Usage, from this folder:
    python run.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # write the image to a file; no window needed
import matplotlib.pyplot as plt
import numpy as np

from model import Params, State, step

STEPS = 500
SEED = 0


def simulate(params: Params, start: State, steps: int, seed: int = SEED):
    """Run the model and return arrays of temperature and heater state."""
    rng = np.random.default_rng(seed)
    temps = [start.temperature]
    heater = [start.heater_on]
    state = start
    for _ in range(steps):
        noise = rng.normal(0.0, params.noise_sd) if params.noise_sd > 0 else 0.0
        state = step(state, params, noise)
        temps.append(state.temperature)
        heater.append(state.heater_on)
    return np.array(temps), np.array(heater)


def main():
    params = Params()
    start = State(temperature=12.0, heater_on=False)
    temps, heater = simulate(params, start, STEPS)

    low = params.setpoint - params.band / 2
    high = params.setpoint + params.band / 2

    # Check the behavior: once the room first reaches the band, does it stay
    # close to it, and does the heater keep cycling?
    first_in = int(np.argmax(temps >= low))
    settled = temps[first_in:]
    switches = int(np.sum(heater[first_in + 1:] != heater[first_in:-1]))
    print(f"Room first reaches the band at step {first_in}")
    print(f"After that: min {settled.min():.2f}, max {settled.max():.2f} "
          f"(band {low:.2f} to {high:.2f})")
    print(f"Heater switched {switches} times after reaching the band")

    t = np.arange(len(temps))
    fig, (ax_t, ax_h) = plt.subplots(
        2, 1, sharex=True, figsize=(8, 5), gridspec_kw={"height_ratios": [3, 1]}
    )
    ax_t.plot(t, temps, label="room temperature")
    ax_t.axhline(params.setpoint, color="black", linewidth=1, label="setpoint")
    ax_t.axhspan(low, high, color="tab:orange", alpha=0.2, label="hysteresis band")
    ax_t.set_ylabel("temperature (°C)")
    ax_t.legend(loc="lower right")
    ax_t.set_title("Bang-bang thermostat with hysteresis")

    ax_h.step(t, heater.astype(int), where="post", color="tab:red")
    ax_h.set_yticks([0, 1], ["off", "on"])
    ax_h.set_ylabel("heater")
    ax_h.set_xlabel("time step")

    fig.tight_layout()
    out = Path(__file__).with_name("thermostat.png")
    fig.savefig(out, dpi=120)
    print(f"Saved {out.name}")


if __name__ == "__main__":
    main()
