import threading
from collections import deque
from dataclasses import field, dataclass

import numpy as np

WINDOW_SECONDS = 5
SAMPLE_RATE = 1000  # Hz
BUF_LEN = int(WINDOW_SECONDS * SAMPLE_RATE)
WINDOW_SIZE = 5  # Number of samples to average
PAD = WINDOW_SIZE // 2


@dataclass
class ADCData:
    """
    Class to hold ADC data and its time stamps.
    """
    _adc_time: deque = field(default_factory=lambda: deque(maxlen=BUF_LEN))
    _adc_queue: deque = field(default_factory=lambda: deque(maxlen=BUF_LEN))
    lock: threading.Lock = field(default_factory=threading.Lock)
    start_time = 0.0

    def append(self, time: float, value: int):
        if self.start_time < 1:
            self.start_time = time
        ref_time = time - self.start_time
        with self.lock:
            self._adc_time.append(ref_time)
            self._adc_queue.append(value)

    def get_snapshot(self) -> tuple[np.ndarray, np.ndarray]:
        """
        To avoid threading issue, we need to copy and lock it to avoid
        race condition.
        """
        with self.lock:
            t = np.array(self._adc_time)
            x = np.array(self._adc_queue)
        return t, x


def moving_average(data: np.ndarray, window_size: int = WINDOW_SIZE) -> np.ndarray:
    """
    Apply a moving average filter to the data.
    :param data: Input data array.
    :param window_size: Size of the moving window.
    :return: Filtered data array.
    """
    if data.size < window_size:
        return data
    kernel = np.ones(window_size) / window_size
    padded_data = np.pad(data, (PAD, PAD), mode='reflect')
    return np.convolve(padded_data, kernel, mode='valid')
