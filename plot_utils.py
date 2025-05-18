import threading

import numpy as np
from matplotlib import pyplot as plt

# Filtration factor
window_size = 5
kernel = np.ones(window_size) / window_size
pad = window_size // 2

# Lock for avoiding race condition
adc_lock = threading.Lock()


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


def get_snapshot(adc_time, adc_queue):
    """
    To avoid threading issue, we need to copy and lock it to avoid race condition.
    :param adc_time:
    :param adc_queue:
    :return: np.asarray, np.asarray
    """
    with adc_lock:
        t = np.array(adc_time)
        x = np.array(adc_queue)
    return t, x


def adc_plot(frame, line, ax, adc_time, adc_queue, window_seconds):
    t_max = adc_time[-1]
    t_min = t_max - window_seconds

    line.set_data(adc_time, adc_queue)
    ax.set_xlim(t_min, t_max)


def diff_plot(frame, line_diff, ax, adc_time, adc_queue, window_seconds):
    dy = np.diff(adc_queue)
    dt = np.diff(adc_time)
    diff = dy / dt

    t_slope = adc_time[1:]
    t_max = t_slope[-1]
    t_min = max(0, t_max - window_seconds)
    line_diff.set_data(t_slope, diff)

    ax.set_xlim(t_min, t_max)


def filtered_plot(frame, line_filtered, ax, adc_time, adc_queue, window_seconds):
    # reflect padding
    padded_data = np.pad(adc_queue, (pad, pad), mode='reflect')
    filtered_data = np.convolve(padded_data, kernel, mode='valid')

    # Create time array for filtered data
    t = np.array(adc_time)
    t_max = t[-1]
    t_min = max(0, t_max - window_seconds)
    line_filtered.set_data(t, filtered_data)
    ax.set_xlim(t_min, t_max)


def filtered_diff_plot(frame, line_diff_filtered, ax, adc_time, adc_queue, window_seconds):
    padded_data = np.pad(adc_queue, (pad, pad), mode='reflect')
    filtered_data = np.convolve(padded_data, kernel, mode='valid')

    # after differentiation, t, x: n-1 sized
    dy = np.diff(filtered_data)
    dt = np.diff(adc_time)
    diff_filtered = dy / dt

    t_slope = adc_time[1:]

    t_max = t_slope[-1]
    t_min = max(0, t_max - window_seconds)
    line_diff_filtered.set_data(t_slope, diff_filtered)

    ax.set_xlim(t_min, t_max)


def update_plots(frame, line, line_diff, line_filtered, line_diff_filtered, axs, adc_time, adc_queue, window_seconds):
    t, x = get_snapshot(adc_time, adc_queue)
    if len(x) < 2: return

    adc_plot(frame, line, axs[0], t, x, window_seconds)
    diff_plot(frame, line_diff, axs[1], t, x, window_seconds)
    filtered_plot(frame, line_filtered, axs[2], t, x, window_seconds)
    filtered_diff_plot(frame, line_diff_filtered, axs[3], t, x, window_seconds)
