"""Run the homeostat, disturb it halfway, and save a plot as homeostat.png.

Drafted by Claude as a starting point. Not yet reviewed by a person.

Two runs from the same starting point:
  1. uniselectors on (both feedback loops)
  2. uniselectors off (first loop only), for comparison

Halfway through each run, unit 0's output polarity is reversed, the way
Ashby disturbed his machine by reversing a connection [unverified against
the book].

Usage, from this folder:
    python run.py            # one run of each kind, plus the plot
    python run.py --batch    # also repeat over 100 random machines (slower)
"""

import sys
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # write the image to a file; no window needed
import matplotlib.pyplot as plt
import numpy as np

from model import N_UNITS, is_stable, make_params, make_state, step

DURATION = 120.0    # total time
DISTURB_AT = 60.0   # when unit 0's polarity is reversed
SETTLED = 0.05      # "at rest" means every needle within this of zero
SEED = 0


def simulate(seed: int, uniselectors_on: bool):
    """Run one machine. Returns times, needle traces, the switch events as
    (time, unit) pairs, and whether the wiring was stable just before the
    disturbance and at the end."""
    params = make_params(seed, uniselectors_on=uniselectors_on)
    state = make_state(seed)
    n_steps = int(round(DURATION / params.dt))
    disturb_step = int(round(DISTURB_AT / params.dt))

    times = [state.time]
    needles = [state.needles]
    switches = []
    stable_before = None
    for k in range(n_steps):
        if k == disturb_step:
            stable_before = is_stable(state, params)
            flipped = params.polarity.copy()
            flipped[0] *= -1
            params = replace(params, polarity=flipped)
        new = step(state, params)
        for unit in np.flatnonzero(new.positions != state.positions):
            switches.append((new.time, int(unit)))
        state = new
        times.append(state.time)
        needles.append(state.needles)
    return (np.array(times), np.array(needles), switches,
            stable_before, is_stable(state, params))


def at_rest(times, needles, start, end):
    """Whether every needle stays near zero over the last 5 time units
    before `end`, and the first time after `start` from which it does."""
    window = (times > end - 5.0) & (times <= end)
    rested = bool(np.all(np.abs(needles[window]) < SETTLED))
    settle_time = None
    if rested:
        segment = (times > start) & (times <= end)
        moving = np.flatnonzero(np.any(np.abs(needles[segment]) >= SETTLED, axis=1))
        idx = moving[-1] + 1 if len(moving) else 0
        settle_time = float(times[segment][idx])
    return rested, settle_time


def report(label, times, needles, switches, stable_before, stable_end):
    before = [s for s in switches if s[0] <= DISTURB_AT]
    after = [s for s in switches if s[0] > DISTURB_AT]
    rest1, t1 = at_rest(times, needles, 0.0, DISTURB_AT)
    rest2, t2 = at_rest(times, needles, DISTURB_AT, DURATION)
    print(f"{label}")
    print(f"  before the disturbance: {len(before)} uniselector steps; "
          f"at rest: {'yes, from t=%.1f' % t1 if rest1 else 'no'}; "
          f"wiring stable: {stable_before}")
    print(f"  after the disturbance:  {len(after)} uniselector steps; "
          f"at rest: {'yes, from t=%.1f' % t2 if rest2 else 'no'}; "
          f"wiring stable: {stable_end}")
    print(f"  final needles: {np.round(needles[-1], 3)}")


def plot_run(ax, times, needles, switches, title, limit=0.8):
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    ax.axhspan(-limit, limit, color="tab:green", alpha=0.08, label="safe range")
    for i in range(N_UNITS):
        ax.plot(times, needles[:, i], color=colors[i], linewidth=1.2, label=f"unit {i}")
    for t, unit in switches:
        ax.plot([t, t], [1.02, 1.1], color=colors[unit], linewidth=1.5)
    ax.axvline(DISTURB_AT, color="black", linestyle="--", linewidth=1)
    ax.text(DISTURB_AT + 0.3, -1.05, "unit 0 reversed", fontsize=8, va="bottom")
    ax.set_ylim(-1.15, 1.15)
    ax.set_ylabel("needle")
    ax.set_title(title, fontsize=10)


def batch(n=100):
    """Repeat over many random machines and count how often each version
    ends at rest."""
    # For each version: [stable wiring before, at rest before,
    #                    stable wiring at end, at rest at end]
    counts = {True: [0, 0, 0, 0], False: [0, 0, 0, 0]}
    steps_needed = []
    initially_stable = 0
    for seed in range(n):
        p = make_params(seed)
        if is_stable(make_state(seed), p):
            initially_stable += 1
        for on in (True, False):
            t, x, sw, stable_before, stable_end = simulate(seed, on)
            counts[on][0] += stable_before
            counts[on][1] += at_rest(t, x, 0.0, DISTURB_AT)[0]
            counts[on][2] += stable_end
            counts[on][3] += at_rest(t, x, DISTURB_AT, DURATION)[0]
            if on:
                steps_needed.append(len(sw))
    print(f"\nOver {n} random machines:")
    print(f"  starting wiring already stable: {initially_stable} of {n}")
    for on, label in ((True, "uniselectors on: "), (False, "uniselectors off:")):
        c = counts[on]
        print(f"  {label} before disturbance: stable wiring {c[0]}, at rest {c[1]}; "
              f"at end: stable wiring {c[2]}, at rest {c[3]}")
    print(f"  uniselector steps per run (on): median {int(np.median(steps_needed))}, "
          f"max {max(steps_needed)}")


def main():
    on = simulate(SEED, uniselectors_on=True)
    off = simulate(SEED, uniselectors_on=False)
    report("Uniselectors on (both feedback loops)", *on)
    report("Uniselectors off (first loop only)", *off)

    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(9, 6.5))
    plot_run(ax1, on[0], on[1], on[2],
             "Uniselectors on: ticks at the top mark each uniselector step")
    plot_run(ax2, off[0], off[1], off[2], "Uniselectors off: first feedback loop only")
    ax2.set_xlabel("time")
    fig.suptitle("Simplified Ashby homeostat, four units")
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, fontsize=8, frameon=False)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    out = Path(__file__).with_name("homeostat.png")
    fig.savefig(out, dpi=120)
    print(f"Saved {out.name}")

    if "--batch" in sys.argv:
        batch()


if __name__ == "__main__":
    main()
