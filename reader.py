import threading
import time

import serial

from model import ADCData

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
SYNC_BIT = 0xAA


def uart_reader(
        buf: ADCData,
        ready_event: threading.Event,
        stop_event: threading.Event):
    """
    Continuous try to open serial port,
    and fill [adc_queue] with latest 13-bit data, [BUF_LEN] samples.
    :param buf: [ADCData] object to hold ADC data, and get lock.
    :param ready_event: [Event] to notify GUI thread to start.
    :param stop_event: [Event] to notify GUI thread to stop.
    :return: None
    """
    while not stop_event.is_set():
        try:
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
                print(f"[✓] Connected to {SERIAL_PORT} @ {BAUD_RATE}")
                buf.start_time = time.time()
                ready_event.set()  # start GUI
                while not stop_event.is_set():
                    # Wait for [SYNC_BIT]
                    byte = ser.read(1)
                    if not byte or byte != SYNC_BIT.to_bytes(1, 'little'):
                        # if read unsuccess or first byte was not 0xAA
                        continue
                    row_data = ser.read(2)
                    if len(row_data) != 2:
                        # Data is not complete
                        print(f'Actual Data received {row_data}')
                        continue
                    adc_value = int.from_bytes(row_data, 'little', signed=False) & 0x0FFF
                    buf.append(time.time(), adc_value)
        except serial.SerialException as e:
            ready_event.clear()
            print(f"[✗] Serial error: {e}, Retrying in 1s..., press CTRL-C to quit")
            time.sleep(1)
