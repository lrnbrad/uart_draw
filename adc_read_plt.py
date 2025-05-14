import queue
import threading
import time

import numpy as np
import serial
from fontTools.merge.util import current_time
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib

matplotlib.use("TkAgg")

''' System Settings '''
PORT = '/dev/ttyACM0'
BAUD_RATE = 115200
SYNC_BIT = 0xAA
MAX_X_POINTS = 10000

''' Shared Objects between Threads '''
adc_queue = queue.Queue()

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
    while not stop_event.is_set():
        try:
            with serial.Serial(port, baudrate, timeout=0.1) as ser:
                print(f"[✓] Connected to {port} @ {baudrate}")
                ready_event.set()  # start GUI
                while not stop_event.is_set():
                    # Wait for [SYNC_BIT]
                    byte = ser.read(1)
                    if not byte or byte != SYNC_BIT.to_bytes():  # if read unsuccess or first byte was not 0xAA
                        print(f'Actual SYNC received {byte}')
                        continue
                    row_data = ser.read(2)
                    if len(row_data) != 2:
                        print(f'Actual Data received {row_data}')
                        continue
                    adc_value = int.from_bytes(row_data, 'little', signed=False) & 0x0FFF
                    print(f"[Debug]: adc_value: {adc_value}")
                    adc_queue.put(adc_value)
        except (serial.SerialException, OSError) as e:
            ready_event.clear()
            print(f"Serial error: {e}, Retrying in 1s..., press CTRL-C to quit")
            time.sleep(1)


# Plot Setup (main thread)
def animator(frame: int):
    """ Update called by FuncAnimation every `interval` seconds.`"""
    n = adc_queue.qsize()  # get size of queue (approx.)

    if n:
        global start_time
        data = np.empty(n, dtype=np.uint16)
        for i in range(n):
            data[i] = adc_queue.get()
        current_time = time.time()
        elapsed_time = [current_time - start_time] * n
        # xs.extend(range(xs[-1] + 1, xs[-1] + 1 + n))
        xs.extend(elapsed_time)
        ys.extend(data)

        # strip to the last MAX_X_POINTS points
        xs_trim = xs[-MAX_X_POINTS:]
        ys_trim = ys[-MAX_X_POINTS:]

        line.set_data(xs_trim, ys_trim)
        ax.set_xlim(xs_trim[0], xs_trim[-1])  # scroll x-axis
    return line,

    # while not adc_queue.empty():
    #
    #     ys.append(adc_queue.get())
    #     xs.append(len(xs))
    # line.set_data(xs[-MAX_X_POINTS:], ys[-MAX_X_POINTS:])  # use both x & y
    # ax.relim()
    # ax.autoscale_view()
    # return line,


if __name__ == '__main__':
    # initialise with a single dummy point
    xs, ys = [0.0], [0]
    reader_thread = threading.Thread(target=uart_reader, daemon=True, name="uart_reader")
    reader_thread.start()
    try:
        # Wait for serial connection
        ready_event.wait()
        start_time = time.time()

        fig, ax = plt.subplots()
        line, = ax.plot([], [])
        ax.set_ylim(0, 4095)
        ax.set_xlabel("Time [s]")
        ax.set_ylabel("ADC value (0~4095)")
        ani = FuncAnimation(fig, animator, interval=50)

        plt.show()
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        reader_thread.join(1)

        # sys.exit(0)
