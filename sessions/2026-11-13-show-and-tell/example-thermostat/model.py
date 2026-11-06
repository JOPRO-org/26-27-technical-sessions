"""A bang-bang thermostat with a hysteresis band.

Drafted by Claude as a starting point. Not yet reviewed by a person.

The model is one room, one heater and one controller. Each time step the
controller reads the room temperature, decides whether the heater should be
on, and the room warms or cools in response.

Nothing here draws a plot. See run.py for that.
"""

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Params:
    setpoint: float = 20.0     # target temperature (degrees C)
    band: float = 1.0          # width of the hysteresis band around the setpoint
    heating_rate: float = 0.1  # degrees added per step while the heater is on
    loss_rate: float = 0.005   # fraction of the indoor-outdoor gap lost per step
    outside: float = 5.0       # outside temperature (degrees C)
    noise_sd: float = 0.0      # standard deviation of sensor noise (0 = none)


@dataclass(frozen=True)
class State:
    temperature: float  # room temperature (degrees C)
    heater_on: bool     # whether the heater is currently running


def step(state: State, params: Params, noise: float = 0.0) -> State:
    """Advance the model by one time step and return the new state.

    `noise` is one sample of sensor noise, supplied by the caller so that
    this function stays pure (same inputs, same output). run.py draws it
    from a normal distribution with standard deviation params.noise_sd.
    """

    # --- Sensor -----------------------------------------------------------
    # The thermometer reports the room temperature, plus any noise.
    reading = state.temperature + noise

    # --- Comparator -------------------------------------------------------
    # Compare the reading with the setpoint. Hysteresis: switch on only
    # below the bottom of the band, switch off only above the top. Inside
    # the band, keep doing whatever we were doing. Without the band the
    # heater would flick on and off every step near the setpoint.
    low = params.setpoint - params.band / 2
    high = params.setpoint + params.band / 2
    if reading < low:
        heater_on = True
    elif reading > high:
        heater_on = False
    else:
        heater_on = state.heater_on

    # --- Effector ---------------------------------------------------------
    # The heater adds a fixed amount of heat per step when it is on.
    heat_in = params.heating_rate if heater_on else 0.0

    # --- Environment ------------------------------------------------------
    # The room loses heat to the outside in proportion to the temperature
    # difference (a simple version of Newton's law of cooling).
    heat_out = params.loss_rate * (state.temperature - params.outside)

    temperature = state.temperature + heat_in - heat_out

    return replace(state, temperature=temperature, heater_on=heater_on)
