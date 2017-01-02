#!/usr/bin/python

# i2c addresses
# Temperature sensor    0x18

from collections import deque
import threading
import Adafruit_MCP9808.MCP9808 as MCP9808

class Temperature(threading.Thread):
    def __init__(self, interval = 0.5, maximum_log_size = 30):
        threading.Thread.__init__(self)
        
        self.running = threading.Event()
        self.interval = interval
        self.log = deque(maxlen = maximum_log_size)
        self.log_mutex = threading.Lock()

        self.sensor = MCP9808.MCP9808() # Default on 0x18
        self.sensor.begin()

    def run(self):
        self._update_temperature_log()
        while not self.running.wait(self.interval):
            self._update_temperature_log()

    def stop(self):
        self.running.set()
        self.join()

    def get_temperature(self):
        with self.log_mutex:
            try:
                temperature = self.log.pop()
                self.log.append(temperature)
                return temperature
            except IndexError:
                return None

    def _update_temperature_log(self):
        temperature = self.sensor.readTempC()
        with self.log_mutex:
            self.log.append(temperature)