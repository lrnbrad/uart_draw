import threading
import time
from collections import deque

import matplotlib
import serial
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

from plot_utils import update_plot, setup_plots

matplotlib.use("TkAgg")

''' System Settings '''
PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
SYNC_BIT = 0xAA

SAMPLE_PERIOD = 0.001  # 1 ms, this related to timer interrupt by STM32
WINDOW_SECONDS = 5
BUF_LEN = int(WINDOW_SECONDS / SAMPLE_PERIOD)

''' Shared Objects between Threads '''
# Queue used for window, use double queue to perform better performance
adc_time = deque(maxlen=BUF_LEN)  # time stamps (seconds)
adc_queue = deque(maxlen=BUF_LEN)  # ADC values (0-4095)

# This event can let the threads know when to start working.
ready_event = threading.Event()
stop_event = threading.Event()

start_time: float = 0.0


# Serial reader thread
def uart_reader(port: str = PORT, baudrate: int = BAUD_RATE):
    """
    Continuous try to open serial port,
    and fill [adc_queue] with latest 13-bit data, 100 samples.
    """
    global start_time
    while not stop_event.is_set():
        try:
            with serial.Serial(port, baudrate, timeout=1) as ser:
                print(f"[✓] Connected to {port} @ {baudrate}")
                start_time = time.time()
                ready_event.set()  # start GUI
                while not stop_event.is_set():
                    # Wait for [SYNC_BIT]
                    byte = ser.read(1)
                    if not byte or byte != SYNC_BIT.to_bytes():
                        # if read unsuccess or first byte was not 0xAA
                        continue
                    row_data = ser.read(2)
                    if len(row_data) != 2:
                        # Data is not complete
                        print(f'Actual Data received {row_data}')
                        continue
                    adc_value = int.from_bytes(row_data, 'little', signed=False) & 0x0FFF
                    # print(f"[Debug]: adc_value: {adc_value}")
                    t = time.time() - start_time
                    adc_time.append(t)
                    adc_queue.append(adc_value)

        except (serial.SerialException, OSError) as e:
            ready_event.clear()
            print(f"Serial error: {e}, Retrying in 1s..., press CTRL-C to quit")
            time.sleep(1)


# Setup plots
fig, axs, line, line_diff = setup_plots()

if __name__ == '__main__':
    # initialise with a single dummy point
    xs, ys = [0.0], [0]
    reader_thread = threading.Thread(target=uart_reader, daemon=True, name="uart_reader")
    reader_thread.start()
    try:
        # Wait for serial connection
        ready_event.wait()
        start_time = time.time()

        ani = FuncAnimation(fig, update_plot,
                            fargs=(line, line_diff, axs, adc_time, adc_queue, WINDOW_SECONDS),
                            interval=40)

        plt.show()
    except (KeyboardInterrupt, SystemExit):
        stop_event.set()
        pass
    finally:
        stop_event.set()
        reader_thread.join(1)

        # sys.exit(0)
