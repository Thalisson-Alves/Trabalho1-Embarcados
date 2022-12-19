from typing import Dict, Optional
import RPi.GPIO as gpio
import adafruit_dht
import board
import time
import threading

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

        self.sensor = adafruit_dht.DHT22(getattr(board, f'D{config.sensors[0].pin}'), use_pulseio=False)
        self.people = 0
        self.alarm_mode = False

        def inc_people(_): self.people += 1
        def dec_people(_): self.people -= 1

        gpio.add_event_detect(self.inputs['Sensor de Contagem de Pessoas Entrada'].pin, gpio.RISING, inc_people, bouncetime=50)
        gpio.add_event_detect(self.inputs['Sensor de Contagem de Pessoas Saída'].pin, gpio.RISING, dec_people, bouncetime=50)

        threading.Thread(target=self.trun_on_ligths_daemon, daemon=True).start()

    def should_sound_buzzer(self) -> bool:
        if self.read_input('Sensor de Fumaça'):
            return True
        return self.alarm_mode and any(self.read_input(name) for name in ('Sensor de Presença', 'Sensor de Janela', 'Sensor de Porta'))

    def trun_on_ligths_daemon(self):
        while True:
            time.sleep(0.01)

            if self.alarm_mode or not self.read_input('Sensor de Presença'):
                continue

            self.set_device('Lâmpada 01', True)
            self.set_device('Lâmpada 02', True)

            time.sleep(15)

            self.set_device('Lâmpada 01', False)
            self.set_device('Lâmpada 02', False)

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
        except (RuntimeError, OverflowError):
            return None

    def read_humidity(self) -> Optional[float]:
        try:
            return self.sensor.humidity
        except (RuntimeError, OverflowError):
            return None

    def read_input(self, name: str) -> bool:
        return self.read_device('inputs', name)

    def read_output(self, name: str) -> bool:
        return self.read_device('outputs', name)

    def read_device(self, device_type: str, name: str) -> bool:
        return bool(gpio.input(getattr(self, device_type)[name].pin))

    def set_device(self, name: str, value: bool):
        print(f'Setting {name} to {int(value)}')
        gpio.output(self.outputs[name].pin, int(value))
