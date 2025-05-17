import numpy as np
from matplotlib import pyplot as plt
from numpy import ndarray

# Filtration factor
window_size = 5
kernel = np.ones(window_size) / window_size
pad = window_size // 2

padded_data:ndarray
filtered_data:ndarray


def setup_plots():
    fig, axs = plt.subplots(4)

    # ADC Plot
    line, = axs[0].plot([], [], linewidth=2)
    axs[0].set_xlabel('Time (s)')
    axs[0].set_ylabel('ADC Value (0~4095)')
    axs[0].set_ylim(0, 4095)

    # Difference Plot
    line_diff, = axs[1].plot([], [], linewidth=2)
    axs[1].set_xlabel('Time (s)')
    axs[1].set_ylabel('Diff Value')
    axs[1].set_ylim(-2000, 2000)

    # Filtered Plot of ADC
    line_filtered, = axs[2].plot([], [], linewidth=2)
    axs[2].set_xlabel('Time (s)')
    axs[2].set_ylabel('Filtered Value (0~4095)')
    axs[2].set_ylim(0, 4095)

    # Difference Plot of Filtered ADC
    line_diff_filtered, = axs[3].plot([], [], linewidth=2)
    axs[3].set_xlabel('Time (s)')
    axs[3].set_ylabel('Diff by Filtered Value')
    axs[3].set_ylim(-2000, 2000)

    return fig, axs, line, line_diff, line_filtered, line_diff_filtered


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
    return line_diff,


def filtered_plot(frame, line_filtered, axs, adc_time, adc_queue, window_seconds):
    data = np.array(adc_queue)
    if len(data) < 2:
        return line_filtered,

    # reflect padding
    global padded_data, filtered_data
    padded_data = np.pad(data, (pad, pad), mode='reflect')
    filtered_data = np.convolve(padded_data, kernel, mode='valid')

    # Create time array for filtered data
    t = np.array(adc_time)
    t_max = t[-1]
    t_min = max(0, t_max - window_seconds)
    line_filtered.set_data(t, filtered_data)
    axs[2].set_xlim(t_min, t_max)
    return line_filtered,


def filtered_diff_plot(frame, line_diff_filtered, axs, adc_time, adc_queue, window_seconds):
    if len(adc_time) < 2:
        return line_diff_filtered,

    # t, x: n sized
    t = np.array(adc_time)
    x = np.array(filtered_data)

    # after differentiation, t, x: n-1 sized
    dx = np.diff(x)
    dt = np.diff(t)
    diff_filtered = dx / dt

    t_slope = t[1:]

    t_max = t_slope[-1]
    t_min = max(0, t_max - window_seconds)
    line_diff_filtered.set_data(t_slope, diff_filtered)

    axs[3].set_xlim(t_min, t_max)
    return line_diff_filtered,


def update_plots(frame, line, line_diff, line_filtered, line_diff_filtered, axs, adc_time, adc_queue, window_seconds):
    adc_plot(frame, line, axs, adc_time, adc_queue, window_seconds)
    diff_plot(frame, line_diff, axs, adc_time, adc_queue, window_seconds)
    filtered_plot(frame, line_filtered, axs, adc_time, adc_queue, window_seconds)
    filtered_diff_plot(frame, line_diff_filtered, axs, adc_time, adc_queue, window_seconds)
