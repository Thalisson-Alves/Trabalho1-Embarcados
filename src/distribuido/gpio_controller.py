from typing import Dict, Optional
import RPi.GPIO as gpio
import adafruit_dht
import board

from distribuido.config import Config
from utils.singleton import SingletonMeta


class GPIOController(metaclass=SingletonMeta):
    def __init__(self) -> None:
        config = Config()

        self.inputs = {
            device.name: device
            for device in config.inputs
        }
        for x in self.inputs.values():
            gpio.setmode(gpio.BCM)
            gpio.setup(x.pin, gpio.IN)

        self.outputs = {
            device.name: device
            for device in config.outputs
        }
        for x in self.outputs.values():
            gpio.setmode(gpio.BCM)
            gpio.setup(x.pin, gpio.OUT)

        self.sensor = adafruit_dht.DHT22(getattr(board, f'D{config.sensors[0].pin}'))

    def read_all_inputs(self) -> Dict[str, bool]:
        return {
            name: self.read_input(name)
            for name in self.inputs
        }

    def read_all_outputs(self) -> Dict[str, bool]:
        return {
            name: self.read_output(name)
            for name in self.outputs
        }

    def read_temperature(self) -> Optional[float]:
        try:
            return self.sensor.temperature
        except RuntimeError:
            return None

    def read_humidity(self) -> Optional[float]:
        try:
            return self.sensor.humidity
        except RuntimeError:
            return None

    def read_input(self, name: str) -> bool:
        return self.read_device('inputs', name)

    def read_output(self, name: str) -> bool:
        return self.read_device('outputs', name)

    def read_device(self, device_type: str, name: str) -> bool:
        return bool(gpio.input(getattr(self, device_type)[name].pin))

    def set_device(self, name: str, value: bool):
        gpio.output(self.outputs[name], value)
