"""A simplified Ashby homeostat: four units with uniselectors.

Drafted by Claude as a starting point. Not yet reviewed by a person.

Each unit has a needle that can swing between -1 and +1. Every needle is
pushed by all four needles (including itself) through weighted connections.
That is the first feedback loop: the units act on each other continuously.

Each unit also has a uniselector, a stepping switch that holds a fixed list
of possible input weights. If a unit's needle swings outside its safe range,
its uniselector steps to the next position, which replaces that unit's
input weights. That is the second feedback loop: when things go badly, the
machine changes its own wiring, blindly, until it finds wiring that keeps
every needle in range.

Nothing here draws a plot. See run.py for that.
"""

from dataclasses import dataclass, replace

import numpy as np

N_UNITS = 4
N_POSITIONS = 25  # Ashby's uniselectors had 25 positions [unverified against the book]


@dataclass(frozen=True)
class Params:
    # The uniselector tables: weights[i, p, j] is the weight from unit j to
    # unit i when unit i's uniselector is at position p. Drawn once, at
    # random, and then fixed, like the wiring inside a real uniselector.
    weights: np.ndarray
    # Polarity of each unit's output (+1 or -1). This is outside the
    # uniselectors' control. The experimenter can flip one to disturb the
    # machine, as Ashby did by reversing a unit's output connection
    # [unverified against the book].
    polarity: np.ndarray
    limit: float = 0.8            # safe range for each needle: -limit to +limit
    switch_interval: float = 0.5  # minimum time between steps of one uniselector
    dt: float = 0.01              # length of one time step
    uniselectors_on: bool = True  # turn the second feedback loop off to compare


@dataclass(frozen=True)
class State:
    needles: np.ndarray    # needle position of each unit, between -1 and +1
    positions: np.ndarray  # current position of each unit's uniselector
    cooldown: np.ndarray   # time until each uniselector may step again
    time: float = 0.0


def make_params(seed: int = 0, **overrides) -> Params:
    """Draw random uniselector tables and return a Params."""
    rng = np.random.default_rng(seed)
    weights = rng.uniform(-1.0, 1.0, size=(N_UNITS, N_POSITIONS, N_UNITS))
    polarity = np.ones(N_UNITS)
    return Params(weights=weights, polarity=polarity, **overrides)


def make_state(seed: int = 0) -> State:
    """Start with the needles at small random positions and all
    uniselectors at position 0."""
    rng = np.random.default_rng(seed + 1000)
    return State(
        needles=rng.uniform(-0.5, 0.5, size=N_UNITS),
        positions=np.zeros(N_UNITS, dtype=int),
        cooldown=np.zeros(N_UNITS),
    )


def connection_matrix(state: State, params: Params) -> np.ndarray:
    """The weights currently in force: row i is what unit i listens to."""
    rows = params.weights[np.arange(N_UNITS), state.positions]  # shape (4, 4)
    return rows * params.polarity[np.newaxis, :]


def step(state: State, params: Params) -> State:
    """Advance the machine by one time step and return the new state."""

    # --- First feedback loop: units acting on each other -----------------
    # Each needle moves in the direction of the weighted sum of all four
    # needles. This is a simplification: Ashby's units also had mass and
    # viscous drag, which this version leaves out.
    w = connection_matrix(state, params)
    velocity = w @ state.needles
    needles = state.needles + params.dt * velocity

    # --- Needle stops -----------------------------------------------------
    # A real needle can only swing so far before it hits the end.
    needles = np.clip(needles, -1.0, 1.0)

    # --- Essential variables ----------------------------------------------
    # Ashby's idea: some variables must stay within limits for the system
    # to survive. Here, each needle's position is an essential variable.
    out_of_range = np.abs(needles) > params.limit

    # --- Second feedback loop: uniselectors -------------------------------
    # A unit whose needle is out of range steps its uniselector, which
    # swaps in a new, random set of input weights. The cooldown stops a
    # uniselector stepping faster than a real stepping switch could.
    cooldown = np.maximum(state.cooldown - params.dt, 0.0)
    positions = state.positions.copy()
    if params.uniselectors_on:
        steps_now = out_of_range & (cooldown <= 0.0)
        positions[steps_now] = (positions[steps_now] + 1) % N_POSITIONS
        cooldown[steps_now] = params.switch_interval

    return replace(
        state,
        needles=needles,
        positions=positions,
        cooldown=cooldown,
        time=state.time + params.dt,
    )


def is_stable(state: State, params: Params) -> bool:
    """Whether the current wiring would bring the needles back to rest on
    its own (all eigenvalues of the connection matrix have negative real
    parts). Used by run.py to check the result, not by the machine."""
    return bool(np.all(np.linalg.eigvals(connection_matrix(state, params)).real < 0))
