from dataclasses import dataclass

import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

matplotlib.use("TkAgg")

from model import moving_average, ADCData, WINDOW_SECONDS

Y_RAW = (0, 4095)
Y_DIFF = (-2000, 2000)


@dataclass
class PlotData:
    """
    Class to hold plot data and its filter function.
    This class is used to update the plot with filtered data.
    :param ax: matplotlib Axes object
    :param line: matplotlib Line2D object
    :param filter_function: function to filter the data,
     you must provide a function that takes timestamp array, row data array or filtered data array
      and returns (x [np.array], y [np.array])
    """
    ax: plt.Axes
    line: plt.Line2D
    filter_function: callable

    def update(self, t, raw, filtered, xlim):
        """
        Apply the filter function to the data and update the plot.
        :param t: timestamp array
        :param raw: raw ADC data
        :param filtered: filtered ADC data
        :param xlim: x-axis limits (range)
        :return: None
        """
        x, y = self.filter_function(t, raw, filtered)
        self.line.set_data(x, y)
        self.ax.set_xlim(xlim)


def _setup_trace(ax, ylabel, ylim, filter_function):
    (line,) = ax.plot([], [], linewidth=2)
    ax.set_ylabel(ylabel)
    ax.set_ylim(*ylim)
    return PlotData(ax, line, filter_function)


def build_traces():
    fig, axs = plt.subplots(4, figsize=(10, 8))
    fig.align_ylabels(axs)
    traces = [
        _setup_trace(
            axs[0], 'ADC Value (0~4095)',
            Y_RAW, lambda t, raw, _: (t, raw)),
        _setup_trace(
            axs[1], 'Diff Value',
            # dy/dt = (y2-y1)/(t2-t1), so we need to shift t by 1
            Y_DIFF, lambda t, raw, _: (t, np.gradient(raw) / np.gradient(t))),
        _setup_trace(
            axs[2], 'Filtered Value (0~4095)',
            Y_RAW, lambda t, _, filtered: (t, filtered)),
        _setup_trace(
            axs[3], 'Diff by Filtered Value',
            # dy/dt = (y2-y1)/(t2-t1), so we need to shift t by 1
            Y_DIFF, lambda t, _, filtered: (t, np.gradient(filtered) / np.gradient(t)))
    ]
    for ax in axs:
        ax.set_xlabel('Time (s)')
    return fig, traces


def run_plot(adc_data: ADCData):
    """
    Run the plot.
    :return: None
    """
    fig, traces = build_traces()

    def animate(frame):
        t, raw = adc_data.get_snapshot()
        if len(t) < 2:
            return [tr.line for tr in traces]
        # This filtered row data is later used in [_setup_trace] to improve reusability,
        # or you want to apply another filter later
        filtered = moving_average(raw)
        t_max = t[-1]
        t_min = max(0, t_max - WINDOW_SECONDS)
        for tr in traces:
            tr.update(t, raw, filtered, (t_min, t_max))
        return [tr.line for tr in traces] + [ax for ax in fig.axes]

    ani = FuncAnimation(fig, animate, interval=40)
    plt.show()
