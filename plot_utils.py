import numpy as np
from matplotlib import pyplot as plt


def setup_plots():
    fig, axs = plt.subplots(2)

    # ADC Plot
    line, = axs[0].plot([], [], linewidth=2)
    axs[0].set_xlabel('Time (s)')
    axs[0].set_ylabel('ADC Value (0~4095)')
    axs[0].set_ylim(0, 4095)

    # Difference Plot
    line_diff, = axs[1].plot([], [], linewidth=2)
    axs[1].set_xlabel('Time (s)')
    axs[1].set_ylabel('Diff Value')

    return fig, axs, line, line_diff


def adc_plot(frame, line, axs, adc_time, adc_queue, window_seconds):
    if not adc_queue:
        return line,

    t_max = adc_time[-1]
    t_min = t_max - window_seconds

    line.set_data(adc_time, adc_queue)
    axs[0].set_xlim(t_min, t_max)
    return line,


def diff_plot(frame, line_diff, axs, adc_time, adc_queue, window_seconds):
    if len(adc_time) < 2:
        return line_diff,

    t = np.array(adc_time)
    x = np.array(adc_queue)

    dx = np.diff(x)
    dt = np.diff(t)
    diff = dx / dt

    t_slope = t[1:]
    t_max = t_slope[-1]
    t_min = max(0, t_max - window_seconds)
    line_diff.set_data(t_slope, diff)

    axs[1].set_xlim(t_min, t_max)
    axs[1].set_ylim(-2000, 2000)
    return line_diff,


def update_plot(frame, line, line_diff, axs, adc_time, adc_queue, window_seconds):
    adc_plot(frame, line, axs, adc_time, adc_queue, window_seconds)
    diff_plot(frame, line_diff, axs, adc_time, adc_queue, window_seconds)
