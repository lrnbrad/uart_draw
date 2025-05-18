import threading

from model import ADCData
from plotting import run_plot
from reader import uart_reader

if __name__ == '__main__':
    adc_data = ADCData()
    ready_event = threading.Event()
    stop_event = threading.Event()

    thread = threading.Thread(target=uart_reader,
                              args=(adc_data, ready_event, stop_event),
                              name="uart_reader", daemon=True)
    thread.start()
    ready_event.wait()  # wait for the reader to be ready
    try:
        run_plot(adc_data)
    except KeyboardInterrupt:
        stop_event.set()
    finally:
        stop_event.set()
        thread.join()
